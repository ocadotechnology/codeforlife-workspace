"""
© Ocado Group
Created on 08/01/2024 at 09:47:25(+00:00).

Validate all contributors have signed the contribution agreement.
"""

import json
import os
import subprocess
import typing as t
from email.utils import parseaddr

Contributors = t.Set[str]

# pylint: disable-next=line-too-long
CONTRIBUTING_FILE_NAME = "CONTRIBUTING.md"
CONTRIBUTORS_HEADER = "### 👨\u200d💻 Contributors 👩\u200d💻"


def get_contributors() -> Contributors:
    """Get authors that have made commits to the current pull request.

    Returns:
        A set of the contributors' email addresses.
    """

    # Navigate to pull request's repo.
    os.chdir("../../../../..")

    pull_request_str = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            "--json",
            "commits",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(pull_request_str)

    pull_request = json.loads(pull_request_str)

    return {
        author["email"]
        for commit in pull_request["commits"]
        for author in commit["authors"]
    }


def get_signed_contributors() -> Contributors:
    """Get the contributors that have signed the contribution agreement.

    Returns:
        A set of the contributors' email addresses.
    """

    with open(
        f"../../../../{CONTRIBUTING_FILE_NAME}",
        "r",
        encoding="utf-8",
    ) as contributing:
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

    signed_contributors = get_signed_contributors()

    contributors = get_contributors()

    assert_contributors(contributors, signed_contributors)


if __name__ == "__main__":
    main()
