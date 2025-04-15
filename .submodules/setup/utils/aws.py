"""
© Ocado Group
Created on 14/04/2025 at 17:06:01(+01:00).
"""

import subprocess
import typing as t
from subprocess import CalledProcessError

from . import pprint


def create_sqs_queue(name: str):
    """Create an SQS queue.

    Args:
        name: The name of the queue.

    Returns:
        A flag designating whether the queue was created.
    """
    pprint.notice("Creating SQS queue...")

    try:
        subprocess.run(
            ["aws", "sqs", "create-queue", f"--queue-name={name}"],
            check=True,
        )

        return True
    except CalledProcessError:
        pprint.error("Failed to create SQS queue.")
        return False


def create_sqs_queues(names: t.Set[str]):
    """Create multiple SQS queues.

    Args:
        names: The names of the SQS queues.

    Returns:
        A flag designating whether any error occurred during the process.
    """
    error = False

    for i, name in enumerate(names, start=1):
        pprint.header(f"Queue ({i}/{len(names)}): {name}")

        created_sqs_queue = create_sqs_queue(name)

        if not error and not created_sqs_queue:
            error = True

        print()

    return error
