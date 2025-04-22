"""
© Ocado Group
Created on 14/04/2025 at 17:06:01(+01:00).
"""

import json
import subprocess
import typing as t
from subprocess import CalledProcessError

from . import pprint


class IAMRole(t.TypedDict):
    """An IAM role."""

    Arn: str


class IAMRoleStatementPrincipal(t.TypedDict):
    """An IAM role statement principal."""

    Service: str


class IAMRoleStatement(t.TypedDict):
    """An IAM role statement."""

    Effect: str
    Action: str
    Principal: IAMRoleStatementPrincipal


class IAMPolicy(t.TypedDict):
    """An IAM policy."""

    Arn: str


class IAMPolicyStatement(t.TypedDict):
    """An IAM policy statement."""

    Effect: str
    Action: str
    Resource: str


class IAMRolePolicy(t.TypedDict):
    """An attachment between an IAM role and policy."""

    Arn: str


class SQSQueueAttributes(t.TypedDict):
    """An SQS queue's attributes."""

    QueueArn: str


def get_iam_role(name: str):
    """Get an IAM role.

    Args:
        name: The name of the IAM role.

    Returns:
        A JSON object or None if not found.
    """
    try:
        stdout = subprocess.run(
            ["aws", "iam", "get-role", f"--role-name={name}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout.decode("utf-8")

        return t.cast(IAMRole, json.loads(stdout)["Role"])
    except CalledProcessError:
        return None


def create_iam_role(name: str, statement: t.List[IAMRoleStatement]):
    """Create an IAM role.

    Args:
        name: The name of the IAM role.
        statement: The definition of the IAM role.

    Returns:
        A JSON object or None if not found.
    """
    pprint.notice("Creating IAM role...")

    assume_role_policy_document = json.dumps(
        {"Version": "2012-10-17", "Statement": statement}
    )

    try:
        stdout = subprocess.run(
            [
                "aws",
                "iam",
                "create-role",
                f"--role-name={name}",
                f"--assume-role-policy-document={assume_role_policy_document}",
            ],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")

        return t.cast(IAMRole, json.loads(stdout)["Role"])
    except CalledProcessError:
        pprint.error("Failed to create IAM role.")
        return None


def get_iam_policy(name: str):
    """Get an IAM policy.

    Args:
        name: The name of the IAM policy.

    Returns:
        A JSON object or None if not found.
    """
    try:
        stdout = subprocess.run(
            [
                "aws",
                "iam",
                "get-policy",
                f"--policy-arn=arn:aws:iam::000000000000:policy/{name}",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout.decode("utf-8")

        return t.cast(IAMPolicy, json.loads(stdout)["Policy"])
    except CalledProcessError:
        return None


def create_iam_policy(name: str, statement: t.List[IAMPolicyStatement]):
    """Create an IAM policy.

    Args:
        name: The name of the IAM policy.
        statement: The definition of the IAM policy.

    Returns:
        A JSON object or None if not found.
    """
    pprint.notice("Creating IAM policy...")

    policy_document = json.dumps({"Version": "2012-10-17", "Statement": statement})

    try:
        stdout = subprocess.run(
            [
                "aws",
                "iam",
                "create-policy",
                f"--policy-name={name}",
                f"--policy-document={policy_document}",
            ],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")

        return t.cast(IAMPolicy, json.loads(stdout)["Policy"])
    except CalledProcessError:
        pprint.error("Failed to create IAM policy.")
        return None


def attach_iam_role_policy(role_name: str, policy_arn: str):
    """Attach a IAM policy to a role.

    Args:
        role_name: The name of the IAM role.
        policy_arn: The ARN of the IAM policy.

    Returns:
        A flag designating whether the policy was attached to the role.
    """
    pprint.notice("Attaching IAM policy to role...")

    try:
        subprocess.run(
            [
                "aws",
                "iam",
                "attach-role-policy",
                f"--role-name={role_name}",
                f"--policy-arn={policy_arn}",
            ],
            check=True,
        )

        return True
    except CalledProcessError:
        pprint.error("Failed to attach IAM policy to role.")
        return False


def create_sqs_queue(name: str):
    """Create an SQS queue.

    Args:
        name: The name of the queue.

    Returns:
        The SQS queue's URL.
    """
    pprint.notice("Creating SQS queue...")

    try:
        stdout = subprocess.run(
            ["aws", "sqs", "create-queue", f"--queue-name={name}"],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")

        return t.cast(str, json.loads(stdout)["QueueUrl"])
    except CalledProcessError:
        pprint.error("Failed to create SQS queue.")
        return None


def get_sqs_queue_attributes(url: str):
    """Get an SQS queue's attributes.

    Args:
        url: The URL of the SQS queue.

    Returns:
        A JSON object or None if not found.
    """
    try:
        stdout = subprocess.run(
            [
                "aws",
                "sqs",
                "get-queue-attributes",
                f"--queue-url={url}",
                "--attribute-names=All",
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout.decode("utf-8")

        return t.cast(SQSQueueAttributes, json.loads(stdout)["Attributes"])
    except CalledProcessError:
        return None


def create_resources(sqs_queue_names: t.Set[str]):
    """Create AWS resources.

    Args:
        sqs_queue_names: The names of the SQS queues to create.

    Returns:
        A flag designating whether any error occurred during the process.
    """
    error = False

    for i, sqs_queue_name in enumerate(sqs_queue_names, start=1):
        pprint.header(f"Queue ({i}/{len(sqs_queue_names)}): {sqs_queue_name}")

        # Get or create SQS queue.
        sqs_queue_url = create_sqs_queue(sqs_queue_name)

        if not error and not sqs_queue_url:
            error = True

        print()

    return error
