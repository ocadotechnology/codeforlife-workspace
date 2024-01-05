"""
© Ocado Group
Created on 05/01/2024 at 14:38:19(+00:00).

Validate a pull request is in the expected state.
"""

import json
import os
import subprocess
import typing as t


def get_inputs():
    """Get the script's inputs.

    Returns:
        A tuple with the values (the PR's number, a flag indicating whether or
        not to validate the PR's latest review state).
    """

    number = int(os.environ["NUMBER"])

    review_state = os.getenv("REVIEW_STATE")
    if review_state == "":
        review_state = None

    return number, review_state


def validate_reviews(number: int, state: t.Optional[str] = None):
    """Validate the PR's reviews.

    Args:
        number: The number of the PR.
        state: The expected latest state.
    """

    view = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            str(number),
            "--json",
            "reviews",
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(view)

    reviews: t.List[t.Dict[str, t.Any]] = json.loads(view)["reviews"]
    reviews.sort(key=lambda review: review["submittedAt"])

    if state is not None:
        assert not reviews or reviews[-1]["state"] != state, (
            "The latest review is not in the expected state."
            f' Latest: "{reviews[-1]["state"]}". Expected: "{state}".'
        )


def main():
    """Run the script."""

    number, review_state = get_inputs()

    # If at least one of the review fields is not None, validate the reviews.
    if any(field is not None for field in [review_state]):
        validate_reviews(number, review_state)


if __name__ == "__main__":
    main()
