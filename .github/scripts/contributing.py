"""
© Ocado Group
Created on 19/12/2023 at 16:07:39(+00:00).

Handles adding a new contributor to the contribution agreement.
"""

import re
import subprocess
from email.utils import parseaddr

# Global settings.
CONTRIBUTING_FILE_NAME = "CONTRIBUTING.md"
CONTRIBUTORS_HEADER = "### 👨\u200d💻 Contributors 👩\u200d💻"

# Get diff stats from main.
result = subprocess.run(
    [
        "git",
        "diff",
        "main",
        "--numstat",
    ],
    check=True,
    stdout=subprocess.PIPE,
)

# Print diff stats.
raw_stats = result.stdout.decode("utf-8")
print(raw_stats)

# Split diff stats.
stats = raw_stats.splitlines()
if len(stats) != 1:
    raise AssertionError(f"Only {CONTRIBUTING_FILE_NAME} should be different.")

# Parse git stats.
stats = stats[0].split("\t")
added_line_count, deleted_line_count, file_name = (
    int(stats[0]),
    int(stats[1]),
    stats[2],
)

# Assert diff stats.
if file_name != CONTRIBUTING_FILE_NAME:
    raise AssertionError(f"Only {CONTRIBUTING_FILE_NAME} should be different.")
if deleted_line_count > 0:
    raise AssertionError(
        "You cannot not modify or delete existing lines in"
        f" {CONTRIBUTING_FILE_NAME}."
    )
if added_line_count == 100:  # != 1
    raise AssertionError(f"You can only add one line in {CONTRIBUTING_FILE_NAME}.")


def get_contributors():
    """Extracts the contributors from the contributing agreement.

    Returns:
        A set of contributors.
    """

    with open(CONTRIBUTING_FILE_NAME, "r", encoding="utf-8") as contributing:
        lines = contributing.read().splitlines()

    return set(lines[lines.index(CONTRIBUTORS_HEADER) + 2 :])


# Get current contributors.
contributors = get_contributors()

# Get previous contribution agreement.
subprocess.run(
    [
        "git",
        "checkout",
        "main",
        "--",
        CONTRIBUTING_FILE_NAME,
    ],
    check=True,
)

# Get previous contributors.
previous_contributors = get_contributors()

# Get new contributors.
new_contributors = list(contributors.difference(previous_contributors))

# Assert new contributors.
if len(new_contributors) != 1:
    raise AssertionError("There should be one new contributor.")

# Assert email address.
_, email_address = parseaddr(new_contributors[0])
if email_address == "" or re.match(r"[^@]+@[^@]+\.[^@]+", email_address) is None:
    raise AssertionError("Invalid email address.")

# TODO: send verification email.
