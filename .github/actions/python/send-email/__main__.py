"""
© Ocado Group
Created on 29/12/2023 at 11:30:49(+00:00).

Using DotDigital, send a transactional email using a triggered campaign as its
content.

https://developer.dotdigital.com/reference/send-transactional-email-using-a-triggered-campaign
"""

import json
import os
import typing as t

import requests

JsonBody = t.Dict[str, t.Any]


def get_settings():
    """_summary_

    Returns:
        _description_
    """

    region = os.getenv("REGION", "")
    assert region != "", "Region path parameter not set."

    auth = os.getenv("AUTH", "")
    assert auth != "", "Authorization header not set."

    timeout = int(os.getenv("TIMEOUT", "-1"))
    assert timeout != -1, "Request timeout not set."

    return region, auth, timeout


def get_json_body() -> JsonBody:
    """_summary_

    Returns:
        _description_
    """

    body: JsonBody = {}

    def set_value(env_key: str, body_key: str, required: bool):
        """Helper to parse environment variables into body parameters.

        Args:
            env_key: The key of the environment variable.
            body_key: The key of the body parameter.
            required: If this value is required in the request.
        """

        raw_value = os.getenv(env_key, "")

        if required:
            assert raw_value != "", f'"{env_key}" environment variable not set.'

        if raw_value != "":
            body[body_key] = json.loads(raw_value)

    set_value(
        env_key="TO_ADDRESSES",
        body_key="toAddresses",
        required=True,
    )
    set_value(
        env_key="CC_ADDRESSES",
        body_key="ccAddresses",
        required=False,
    )
    set_value(
        env_key="BCC_ADDRESSES",
        body_key="bccAddresses",
        required=False,
    )
    set_value(
        env_key="FROM_ADDRESS",
        body_key="fromAddress",
        required=False,
    )
    set_value(
        env_key="CAMPAIGN_ID",
        body_key="campaignId",
        required=True,
    )
    set_value(
        env_key="PERSONALIZATION_VALUES",
        body_key="personalizationValues",
        required=False,
    )
    set_value(
        env_key="METADATA",
        body_key="metadata",
        required=False,
    )
    set_value(
        env_key="ATTACHMENTS",
        body_key="attachments",
        required=False,
    )

    return body


def send_email(region: str, auth: str, timeout: int, body: JsonBody):
    """_summary_

    Args:
        region: _description_
        auth: _description_
        timeout: _description_
        body: _description_
    """

    response = requests.post(
        url=f"https://{region}-api.dotdigital.com/v2/email/triggered-campaign",
        json=body,
        headers={
            "accept": "text/plain",
            "authorization": auth,
        },
        timeout=timeout,
    )

    assert response.ok, response.json()


def main():
    """Entry point"""

    raise Exception("abc")

    region, auth, timeout = get_settings()
    body = get_json_body()
    send_email(region, auth, timeout, body)


if __name__ == "__main__":
    main()