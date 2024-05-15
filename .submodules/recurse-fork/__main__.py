"""
© Ocado Group
Created on 13/05/2024 at 16:20:50(+01:00).

Setup the CFL workspace for contributors by recursively forking submodules.
"""

import json
import re
import subprocess
import typing as t
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError

from colorama import Fore, Style
from colorama import init as colorama_init

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Submodule:
    """A Git submodule definition found in the file: .gitmodules."""

    path: str
    url: str


def read_submodules() -> t.Dict[str, Submodule]:
    """Read the submodules from .gitmodules (located at the workspace's root).

    Returns:
        A dict where the key is the name of the submodule and value is an object
        of the submodule's attributes.
    """
    with open(BASE_DIR / ".gitmodules", "r", encoding="utf-8") as gitmodules:
        gitmodules_str = gitmodules.read()

    # [1:] to skip initial blank string.
    gitmodules_lines: t.List[str] = re.split(
        r'^\[submodule \"(.*)"\]$',
        gitmodules_str,
        flags=re.MULTILINE,
    )[1:]

    # Group the strings as key-value pairs, where the key is the submodule's
    # name and the value is the raw string.
    submodule_strs = dict(zip(gitmodules_lines[::2], gitmodules_lines[1::2]))

    return {
        name: Submodule(
            **dict(
                line.strip().split(" = ", maxsplit=1)
                for line in submodule_str.splitlines()[1:]
            )
        )
        for name, submodule_str in submodule_strs.items()
    }


def login_to_github():
    """Log into GitHub with the CLI.

    https://cli.github.com/manual/gh_auth_login
    """
    subprocess.run(
        ["gh", "auth", "login", "--web"],
        check=True,
    )


def fork_repo(name: str, url: str):
    """Fork a repo on GitHub.

    https://cli.github.com/manual/gh_repo_fork

    Args:
        owner: The owner of the repo to fork.
        name: The name of the repo to fork.
    """
    print(Style.BRIGHT + f'Forking repo "{name}".' + Style.RESET_ALL)

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
        pass


def clone_repo(name: str, path: str):
    """Clone a repo from GitHub.

    https://cli.github.com/manual/gh_repo_clone

    Args:
        name: The name of the repo to clone.
    """
    print(Style.BRIGHT + f'Cloning repo "{name}".' + Style.RESET_ALL)

    try:
        subprocess.run(
            ["gh", "repo", "clone", name, str(BASE_DIR / path)],
            check=True,
        )
    except CalledProcessError:
        pass


def view_repo(name: str):
    """Print a repo on GitHub as a JSON object.

    https://cli.github.com/manual/gh_repo_view

    Args:
        name: The name of the repo to view.
    """
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

    repo = json.loads(repo_str)

    print(
        Style.BRIGHT
        + "Viewing repo"
        + (f' "{name}"' if name else "")
        + "."
        + Style.RESET_ALL
    )
    print(json.dumps(repo, indent=2))


def main() -> None:
    """Entry point."""
    colorama_init()

    submodules = read_submodules()

    login_to_github()

    for name, submodule in submodules.items():
        fork_repo(name, submodule.url)

        clone_repo(name, submodule.path)

        view_repo(name)

    print(Style.BRIGHT + Fore.GREEN + "Setup completed." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
