"""
© Ocado Group
Created on 10/01/2024 at 17:16:57(+00:00).

Notify all contributors that a new version of the contribution agreement has
been released.
"""

import os
import typing as t
from email.utils import parseaddr

import requests

Contributors = t.Set[str]

CONTRIBUTORS_HEADER = "### 👨\u200d💻 Contributors 👩\u200d💻"
CAMPAIGN_ID = 1512393


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
        "../../../../CONTRIBUTING.md",
        "r",
        encoding="utf-8",
    ) as contributing:
        lines = contributing.read().splitlines()

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

    auth = get_inputs()

    contributors = get_contributors()

    send_emails(auth, contributors)


if __name__ == "__main__":
    main()
