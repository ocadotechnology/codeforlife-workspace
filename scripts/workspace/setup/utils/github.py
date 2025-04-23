"""
© Ocado Group
Created on 14/04/2025 at 16:45:06(+01:00).
"""

import json
import os
import subprocess
import typing as t
from shutil import rmtree
from subprocess import CalledProcessError
from time import sleep

import inquirer  # type: ignore[import-untyped]

from . import pprint
from .git import SubmoduleDict
from .settings import WORKSPACE_DIR


def login():
    """Login to GitHub with the CLI.

    https://cli.github.com/manual/gh_auth_status
    https://cli.github.com/manual/gh_auth_logout
    https://cli.github.com/manual/gh_auth_login
    """
    pprint.notice("Checking if you are logged into GitHub...")

    logged_in = True

    try:
        subprocess.run(
            ["gh", "auth", "status"],
            check=True,
        )
    except CalledProcessError:
        logged_in = False

    if logged_in:
        answers = inquirer.prompt(
            [
                inquirer.Confirm(
                    "stay_logged_in",
                    message="Continue with logged in account?",
                )
            ]
        )

        if answers:
            logged_in = t.cast(bool, answers["stay_logged_in"])

        if not logged_in:
            subprocess.run(
                ["gh", "auth", "logout"],
                check=True,
            )

    if not logged_in:
        subprocess.run(
            ["gh", "auth", "login", "--web", "--git-protocol=https"],
            check=True,
        )


def fork_repo(url: str):
    """Fork a repo on GitHub.

    https://cli.github.com/manual/gh_repo_fork

    Args:
        owner: The owner of the repo to fork.
        name: The name of the repo to fork.

    Returns:
        A flag designating whether the repo was successfully forked.
    """
    pprint.notice("Forking repo...")

    try:
        subprocess.run(
            [
                "gh",
                "repo",
                "fork",
                url,
                "--default-branch-only",
                "--clone=false",
            ],
            check=True,
        )
    except CalledProcessError:
        pprint.error("Failed to fork repo.")
        return False

    return True


def clone_repo(name: str, path: str):
    # pylint: disable=line-too-long
    """Clone a repo from GitHub.

    https://cli.github.com/manual/gh_repo_clone

    Args:
        name: The name of the repo to clone.
        path: The paths to clone the repo to.

    Returns:
        A flag designating whether the repo was successfully cloned.
    """
    # pylint: enable=line-too-long
    pprint.notice("Cloning repo...")

    repo_dir = str(WORKSPACE_DIR / path)

    if os.path.isdir(repo_dir) and os.listdir(repo_dir):
        pprint.notice(f"{repo_dir} already exists.")

        answers = inquirer.prompt(
            [
                inquirer.Confirm(
                    "overwrite",
                    message=(
                        "Delete the repo's current directory and clone the repo in"
                        " the directory?"
                    ),
                )
            ]
        )

        if not answers or not t.cast(bool, answers["overwrite"]):
            return True

        rmtree(repo_dir)

    max_attempts = 5
    retry_delay = 1
    retry_attempts = max_attempts - 1
    for attempt_index in range(max_attempts):
        try:
            subprocess.run(
                ["gh", "repo", "clone", name, repo_dir],
                check=True,
            )

            return True
        except CalledProcessError:
            if os.path.isdir(repo_dir):
                rmtree(repo_dir)

            if attempt_index != retry_attempts:
                pprint.warn(
                    f"Retrying clone in {retry_delay} seconds."
                    + f" Attempt {attempt_index + 1}/{retry_attempts}."
                )

                sleep(retry_delay)
                retry_delay *= 2

    pprint.error("Failed to clone repo.")

    return False


def view_repo(name: str):
    """Print a repo on GitHub as a JSON object.

    https://cli.github.com/manual/gh_repo_view

    Args:
        name: The name of the repo to view.
    """
    pprint.notice("Viewing repo...")

    try:
        repo_str = subprocess.run(
            [
                "gh",
                "repo",
                "view",
                name,
                "--json=" + ",".join(["name", "url", "createdAt", "isFork"]),
            ],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")
    except CalledProcessError:
        pprint.warn("Failed to view repo.")
        return

    repo = json.loads(repo_str)
    print(json.dumps(repo, indent=2))


def fork_and_clone_repos(submodules: SubmoduleDict):
    """Fork and clone each submodule's repo.

    Args:
        submodules: The submodules to fork and clone.

    Returns:
        A flag designating whether an error occurred during the process.
    """
    error = False

    for i, (name, submodule) in enumerate(submodules.items(), start=1):
        pprint.header(f"Submodule ({i}/{len(submodules)}): {name}")

        forked_repo = fork_repo(submodule.url)

        cloned_repo = False
        if forked_repo:
            cloned_repo = clone_repo(name, submodule.path)

            view_repo(name)

        if not error and (not forked_repo or not cloned_repo):
            error = True

        print()

    return error
