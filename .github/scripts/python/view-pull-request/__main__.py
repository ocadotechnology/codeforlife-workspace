"""
© Ocado Group
Created on 05/01/2024 at 14:38:19(+00:00).

View a GitHub pull request. Optionally, you can also validate a pull request's
state.
"""

import json
import os
import subprocess
import typing as t

PullRequest = t.Dict[str, t.Any]


def get_inputs():
    """Get the script's inputs.

    Returns:
        A tuple with the values (the PR's number, the PR's fields to output to
        github, a flag indicating whether or not to validate the PR's latest
        review state).
    """

    number = int(os.environ["NUMBER"])

    outputs = os.getenv("OUTPUTS", "").split(",")
    outputs = [output.lower() for output in outputs if output != ""]

    review_state = os.getenv("REVIEW_STATE")
    if review_state == "":
        review_state = None

    return number, outputs, review_state


def get_pull_request(number: int, fields: t.List[str]) -> PullRequest:
    """Gets the pull request object with the specified fields.

    Args:
        number: The number of the PR.
        fields: A the PR's fields to retrieve.

    Returns:
        The pull request as a JSON object.
    """

    pull_request = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            str(number),
            "--json",
            ",".join(fields),
        ],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    print(pull_request)

    return json.loads(pull_request)


def validate_reviews(pull_request: PullRequest, state: t.Optional[str] = None):
    """Validate the PR's reviews.

    Args:
        pull_request: The pull request.
        state: The expected latest state.
    """

    # If all of the review fields is None, there's nothing to validate.
    if all(field is None for field in [state]):
        return

    reviews: t.List[t.Dict[str, t.Any]] = pull_request["reviews"]
    reviews.sort(key=lambda review: review["submittedAt"])

    if state is not None:
        assert reviews, "The pull request has not been reviewed."
        assert reviews[-1]["state"] == state, (
            "The latest review is not in the expected state."
            f' Latest: "{reviews[-1]["state"]}". Expected: "{state}".'
        )


# TODO: create a codeforlife.ci submodule for all CI helpers.
def write_to_github_output(**outputs: str):
    """Write to GitHub's output."""

    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as github_out:
        github_out.write(
            "\n".join([f"{key}={value}" for key, value in outputs.items()])
        )


def main():
    """Run the script."""

    number, outputs, review_state = get_inputs()

    pull_request_fields = outputs.copy()

    # If we're validating a field but not outputting it, we still need to get
    #   the field to validate it.
    if review_state is not None and "reviews" not in outputs:
        pull_request_fields.append("reviews")

    pull_request = get_pull_request(number, pull_request_fields)

    validate_reviews(pull_request, review_state)

    write_to_github_output(
        **{
            output.replace("-", "_").upper(): str(pull_request[output])
            for output in outputs
        }
    )


if __name__ == "__main__":
    main()
