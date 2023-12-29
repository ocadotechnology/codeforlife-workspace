"""
© Ocado Group
Created on 19/12/2023 at 16:07:39(+00:00).

Handles adding a new contributor to the contribution agreement.
"""

import os
import re
import subprocess
from email.utils import parseaddr

import requests

# Global settings.
CONTRIBUTING_FILE_NAME = "CONTRIBUTING.md"
CONTRIBUTING_FILE_PATH = f"../../../{CONTRIBUTING_FILE_NAME}"
CONTRIBUTORS_HEADER = "### 👨\u200d💻 Contributors 👩\u200d💻"


def get_starter_info():
    """Gets the info needed to start this script.

    Returns:
        A tuple where the values are (the URL of the pull request, the
        DotDigital API user's authorization).
    """

    pr_url = os.getenv("PR_URL")
    assert pr_url is not None, "Pull request URL environment variable not set."

    # dd_api_user_email_address = os.getenv("DOTDIGITAL_API_USER_EMAIL_ADDRESS")
    # assert (
    #     dd_api_user_email_address is not None
    # ), "DotDigital API user email address environment variable not set."

    # dd_api_user_password = os.getenv("DOTDIGITAL_API_USER_PASSWORD")
    # assert (
    #     dd_api_user_password is not None
    # ), "DotDigital API user password environment variable not set."

    dd_api_user_auth = os.getenv("DOTDIGITAL_API_USER_AUTH")
    assert (
        dd_api_user_auth is not None
    ), "DotDigital API user authorization environment variable not set."

    return pr_url, dd_api_user_auth


def fetch_main_branch():
    """Fetch main branch from origin."""

    subprocess.run(
        [
            "git",
            "fetch",
            "origin",
            "new_contributor_validations:new_contributor_validations",  # TODO: use main
        ],
        check=True,
    )


def assert_diff_stats():
    """Assert that only the contribution agreement is different and only one
    line was added to the contribution agreement.
    """

    # Get raw diff stats from main.
    diff_stats_str = subprocess.run(
        [
            "git",
            "diff",
            "new_contributor_validations",  # TODO: use main
            "--numstat",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(f'Diff Stats: "{diff_stats_str}"')

    # Get diff stats per file.
    diff_stats_per_file = diff_stats_str.splitlines()
    assert (
        len(diff_stats_per_file) == 1
    ), f"Only {CONTRIBUTING_FILE_NAME} should be different."

    # Parse and assert diff stats.
    diff_stats = diff_stats_per_file[0].split("\t")
    assert (
        diff_stats[2] == CONTRIBUTING_FILE_NAME
    ), f"Only {CONTRIBUTING_FILE_NAME} should be different."
    assert (
        int(diff_stats[1]) == 0
    ), "You cannot modify or delete existing lines."
    assert int(diff_stats[0]) == 1, "You must add just one line."


def get_diff_line():
    """Get the one differing line from the contribution agreement. Asserts that
    the line is located in the list of contributors.

    Returns:
        The one-based index and string of the one differing line from the
        contribution agreement.
    """

    # Easier to parse diff stats for assertions.
    assert_diff_stats()

    # Get raw diff from main.
    diff_str = subprocess.run(
        [
            "git",
            "--no-pager",
            "diff",
            "new_contributor_validations",  # TODO: use main
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(f'Diff: "{diff_str}"')

    # Match the diff line range.
    diff_line_range = re.match(
        r".*\@\@ -(\d+),(\d+) \+(\d+),(\d+) \@\@.*",
        diff_str,
        flags=re.DOTALL,
    )
    assert diff_line_range is not None, "Failed to match line-difference range."

    # Assert diff line range is of size one.
    original_line_start = int(diff_line_range.group(1))
    new_line_start = int(diff_line_range.group(3))
    assert original_line_start == new_line_start, "Line starts must be equal."

    original_line_count = int(diff_line_range.group(2))
    new_line_count = int(diff_line_range.group(4))
    assert (
        new_line_count - original_line_count == 1
    ), "One line should be different."

    diff_line_index = original_line_start + original_line_count

    # Split contribution agreement into lines.
    with open(CONTRIBUTING_FILE_PATH, "r", encoding="utf-8") as contributing:
        lines = contributing.read().splitlines()

    # Assert diff line is after the contributors header.
    # NOTE: -1 to convert 1 based indexing to 0.
    # NOTE: +1 because there should be a space after the header.
    assert (
        diff_line_index - 1 > lines.index(CONTRIBUTORS_HEADER) + 1
    ), "Contributor must be added to the list of contributors."

    diff_line = lines[diff_line_index - 1]

    print(f'Diff Line: "{diff_line}"')

    return diff_line_index, diff_line


def get_email_address(diff_line_index: int, diff_line: str):
    """Get the email address from the diff line. Assert that the email address
    used to sign the commit is the same as the signed email address.

    Args:
        diff_line_index: The one-based index of the differing line in the
            contribution agreement.
        diff_line: The differing line in the contribution agreement.

    Returns:
        The new contributor's email address.
    """

    # Get and assert the signed email address format.
    _, signed_email_address = parseaddr(diff_line)
    assert (
        signed_email_address != ""
        and re.match(r"[^@]+@[^@]+\.[^@]+", signed_email_address) is not None
    ), "Invalid email address format."

    blame = subprocess.run(
        [
            "git",
            "blame",
            "-L",
            f"{diff_line_index},{diff_line_index}",
            CONTRIBUTING_FILE_PATH,
            "--show-email",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(f'Blame: "{blame}"')

    # Assert commit's author.
    commit_author = re.match(rf".+ \(<(.+)> .+\) {re.escape(diff_line)}", blame)
    assert (
        commit_author is not None
    ), "Failed to match commit author from git blame."

    commit_author_email_address = commit_author.group(1)
    assert (
        signed_email_address.lower() == commit_author_email_address.lower()
    ), "The signed email address must be equal to the commit author's."

    return signed_email_address


def send_verify_new_contributor_email(
    pr_url: str,
    dd_api_user_auth: str,
    email_address: str,
):
    """Send an email to verify that the new contributor owns the email address.

    https://developer.dotdigital.com/reference/send-transactional-email-using-a-triggered-campaign

    Args:
        pr_url: The URL of the pull request.
        dd_api_user_auth: The DotDigital API user's authorization.
        email_address: The new contributor's email address.
    """

    response = requests.post(
        url="https://r1-api.dotdigital.com/v2/email/triggered-campaign",
        json={
            "campaignId": 1506387,
            "toAddresses": [
                email_address,
            ],
            "personalizationValues": [
                {
                    "name": "PR_URL",
                    "value": pr_url,
                },
            ],
        },
        headers={
            "accept": "text/plain",
            "authorization": dd_api_user_auth,
        },
        timeout=60,
    )

    assert response.ok, response.json()


def main():
    """Runs the scripts."""

    os.environ["HELLO"] = "WORLD!!!"

    # pr_url, dd_api_user_auth = get_starter_info()

    # fetch_main_branch()

    # diff_line_index, diff_line = get_diff_line()

    # email_address = get_email_address(diff_line_index, diff_line)

    # send_verify_new_contributor_email(
    #     pr_url,
    #     dd_api_user_auth,
    #     email_address="stefan.kairinos@ocado.com",
    # )


if __name__ == "__main__":
    main()
