"""
© Ocado Group
Created on 10/01/2024 at 17:16:57(+00:00).

Notify all contributors that a new version of the contribution agreement has
been released.
"""

import os
import re
import subprocess
import typing as t
from email.utils import parseaddr

import requests

Contributors = t.Set[str]

CONTRIBUTING_FILE_NAME = "CONTRIBUTING.md"
AGREEMENT_END_LINE = "## Become a Contributor"
CONTRIBUTORS_HEADER = "### 👨\u200d💻 Contributors 👩\u200d💻"
CAMPAIGN_ID = 1512393


def get_previous_agreement_end_line_index():
    """Get the index of the previous agreement's end line.

    Returns:
        The index of the previous agreement's end line.
    """

    # Get previous agreement.
    previous_contributing = subprocess.run(
        [
            "git",
            "--no-pager",
            "show",
            f"HEAD~1:{CONTRIBUTING_FILE_NAME}",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(previous_contributing)

    # Get index of line where previous agreement ended.
    # NOTE: +1 to convert 0 based indexing to 1.
    return previous_contributing.splitlines().index(AGREEMENT_END_LINE) + 1


def agreement_is_different():
    """Checks that the contributor agreement is different.

    Returns:
        A flag designating if the contributor agreement is different.
    """

    # Get diff file names.
    diff_output = subprocess.run(
        [
            "git",
            "--no-pager",
            "diff",
            "--name-only",
            "HEAD~1",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(diff_output)

    # Check if the contributing file is different.
    if all(file != CONTRIBUTING_FILE_NAME for file in diff_output.splitlines()):
        print(f"{CONTRIBUTING_FILE_NAME} is not different.")
        return False

    previous_agreement_end_line_index = get_previous_agreement_end_line_index()

    # Get diff between current and previous contributing file.
    diff_output = subprocess.run(
        [
            "git",
            "--no-pager",
            "diff",
            f"HEAD~1:{CONTRIBUTING_FILE_NAME}",
            CONTRIBUTING_FILE_NAME,
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(diff_output)

    # Split diffs following git's diff format.
    # NOTE: We're capturing the index of the diff's start line.
    # NOTE: [1:] because we don't need the diff context info.
    diffs = re.split(
        r"^\@\@ -(\d+),\d+ \+\d+,\d+ \@\@.*$\n",
        diff_output,
        flags=re.MULTILINE,
    )[1:]

    # Parse the split diff-data.
    for diff_start_line_index, diff in zip(
        [int(diff_start_line_index) for diff_start_line_index in diffs[::2]],
        diffs[1::2],
    ):
        # Only want to know which lines were removed or edited.
        diff_lines = [line for line in diff.splitlines() if not line.startswith("+")]

        try:
            # Get index of first line that was removed or edited in previous file.
            diff_line_index = next(
                diff_start_line_index + diff_line_index
                for diff_line_index, diff_line in enumerate(diff_lines)
                if diff_line.startswith("-")
            )

            # Check if line came before the end of the agreement.
            if diff_line_index < previous_agreement_end_line_index:
                return True

        except StopIteration:
            pass

    print("All differences are after the end of the agreement.")
    return False


def get_inputs():
    """Get script's inputs.

    Returns:
        The auth header used when making requests to DotDigital's API.
    """

    auth = os.environ["AUTH"]

    return auth


def get_contributors() -> Contributors:
    """Gets the contributors' email addresses.

    Returns:
        A set of the contributors' email addresses.
    """

    with open(
        f"../../../../{CONTRIBUTING_FILE_NAME}",
        "r",
        encoding="utf-8",
    ) as contributing:
        lines = contributing.read().splitlines()

    # NOTE: +2 because we don't want the header or the space after it.
    return {
        parseaddr(contributor)[1]
        for contributor in lines[lines.index(CONTRIBUTORS_HEADER) + 2 :]
    }


def send_emails(auth: str, contributors: Contributors):
    """Send an email to all contributors that a new version of the contribution
    agreement has been released.

    Args:
        auth: The auth header used when making requests to DotDigital's API.
        contributors: The email addresses to send the email to.
    """

    failed_sends = False

    for contributor in contributors:
        try:
            response = requests.post(
                url="https://r1-api.dotdigital.com/v2/email/triggered-campaign",
                headers={
                    "accept": "text/plain",
                    "authorization": auth,
                },
                json={
                    "campaignId": CAMPAIGN_ID,
                    "toAddresses": [contributor],
                },
                timeout=30,
            )

            assert response.ok, response.json()

            print(f"✅ Sent email to {contributor}.")

        # pylint: disable-next=broad-exception-caught
        except Exception as ex:
            print(f'❌ Failed to send email to {contributor} due to exception: "{ex}".')

            failed_sends = True

    assert not failed_sends, "Failed to send emails to some contributors."


def main():
    """Entry point."""

    if agreement_is_different():
        auth = get_inputs()

        contributors = get_contributors()

        send_emails(auth, contributors)


if __name__ == "__main__":
    main()
