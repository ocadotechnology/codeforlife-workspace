"""
© Ocado Group
Created on 08/01/2024 at 09:47:25(+00:00).

Validate all contributors have signed the contribution agreement.
"""

import os
import subprocess
import typing as t
from email.utils import parseaddr

Contributors = t.Set[str]

# pylint: disable-next=line-too-long
CONTRIBUTING_FILE_NAME = "CONTRIBUTING.md"
CONTRIBUTING_FILE_PATH = f"../../../../{CONTRIBUTING_FILE_NAME}"
CONTRIBUTORS_HEADER = "### 👨\u200d💻 Contributors 👩\u200d💻"


def get_inputs():
    """Get the script's inputs.

    Returns:
        A tuple with the values:
            repo: The repository the pull request was made to.
            pr_num: The pull request's number.
            prod_branch: The name of the production branch. Defaults to
                production.
    """

    repo = os.environ["REPO"]
    pr_num = int(os.environ["PR_NUM"])
    prod_branch = os.getenv("PROD_BRANCH", "production")

    return repo, pr_num, prod_branch


def checkout_pull_request(repo: str, num: int):
    """Checkout the pull request.

    Args:
        repo: The pull request's repository.
        num: The pull request's number.
    """

    subprocess.run(
        [
            "gh",
            "pr",
            "checkout",
            str(num),
            "--repo",
            repo,
        ],
        check=True,
    )


def fetch_prod_branch(prod_branch: str):
    """Fetches the production branch.

    Args:
        prod_branch: The name of the production branch.
    """

    os.chdir("../../../../..")

    print(os.getcwd())

    subprocess.run(
        [
            "git",
            "fetch",
            "origin",
            f"{prod_branch}:{prod_branch}",
        ],
        check=True,
    )


def get_contributors(prod_branch: str) -> Contributors:
    """Get the contributors that have made changes to the current branch.

    Args:
        prod_branch: The name of the production branch.

    Returns:
        A set of the contributors' email addresses.
    """

    shortlog = subprocess.run(
        [
            "git",
            "shortlog",
            "--summary",
            "--numbered",
            "--email",
            f"{prod_branch}..HEAD",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(shortlog)

    return {parseaddr(log.split("\t")[1])[1] for log in shortlog.splitlines()}


def get_signed_contributors() -> Contributors:
    """Get the contributors that have signed the contribution agreement.

    Returns:
        A set of the contributors' email addresses.
    """

    with open(CONTRIBUTING_FILE_PATH, "r", encoding="utf-8") as contributing:
        lines = contributing.read().splitlines()

    # NOTE: +2 because we don't want the header and its proceeding blank line.
    lines = lines[lines.index(CONTRIBUTORS_HEADER) + 2 :]

    return {parseaddr(line)[1] for line in lines}


def assert_contributors(
    contributors: Contributors,
    signed_contributors: Contributors,
):
    """Assert that all contributors have signed the contribution agreement.

    Args:
        contributors: The contributors that have made changes to the current
            branch.
        signed_contributors: The contributors that have signed the contribution
            agreement.
    """

    unsigned_contributors = contributors.difference(signed_contributors)

    assert not unsigned_contributors, (
        "The following contributors have not signed the agreement:"
        f" {', '.join(unsigned_contributors)}."
    )


def main():
    """Entry point."""

    repo, pr_num, prod_branch = get_inputs()

    signed_contributors = get_signed_contributors()

    # checkout_pull_request(repo, pr_num)

    fetch_prod_branch(prod_branch)

    contributors = get_contributors(prod_branch)

    assert_contributors(contributors, signed_contributors)


if __name__ == "__main__":
    main()
