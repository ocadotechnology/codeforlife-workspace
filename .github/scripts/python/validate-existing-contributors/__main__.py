"""
© Ocado Group
Created on 08/01/2024 at 09:47:25(+00:00).

Validate all contributors have signed the contribution agreement.
"""

import json
import os
import typing as t
from email.utils import parseaddr

PullRequest = t.Dict[str, t.Any]
Contributors = t.Set[str]

# pylint: disable-next=line-too-long
CONTRIBUTING_FILE_NAME = "CONTRIBUTING.md"
CONTRIBUTORS_HEADER = "### 👨\u200d💻 Contributors 👩\u200d💻"
BOTS = {
    "49699333+dependabot[bot]@users.noreply.github.com",
}


def get_inputs():
    """Get script's inputs.

    Returns:
        A JSON object of the pull request.
    """

    pull_request: PullRequest = json.loads(os.environ["PULL_REQUEST"])

    return pull_request


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

    return {parseaddr(line)[1].lower() for line in lines}


def assert_contributors(
    pull_request: PullRequest,
    signed_contributors: Contributors,
):
    """Assert that all contributors have signed the contribution agreement.

    Args:
        pull_request: The JSON object of the pull request.
        signed_contributors: The contributors that have signed the contribution
            agreement.
    """

    contributors: Contributors = {
        author["email"].lower()
        for commit in pull_request["commits"]
        for author in commit["authors"]
    }

    unsigned_contributors = contributors.difference(
        signed_contributors.union(BOTS),
    )

    assert not unsigned_contributors, (
        "The following contributors have not signed the agreement:"
        f" {', '.join(unsigned_contributors)}."
    )


def main():
    """Entry point."""

    pull_request = get_inputs()

    signed_contributors = get_signed_contributors()

    assert_contributors(pull_request, signed_contributors)


if __name__ == "__main__":
    main()
