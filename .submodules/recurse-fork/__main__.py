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


@dataclass(frozen=True)
class Repo:
    """A GitHub repo."""

    @dataclass(frozen=True)
    class Owner:
        """The owner of a GitHub repo."""

        id: str
        login: str

    # pylint: disable=invalid-name
    owner: t.Optional[Owner] = None
    createdAt: t.Optional[str] = None
    isFork: t.Optional[bool] = None
    url: t.Optional[str] = None
    name: t.Optional[str] = None
    # pylint: enable=invalid-name


def login_to_github():
    """Log into GitHub with the CLI.

    https://cli.github.com/manual/gh_auth_login
    """
    subprocess.run(
        ["gh", "auth", "login", "--web"],
        check=True,
    )


def view_repo(
    fields: t.List[str],
    name: t.Optional[str] = None,
    print_json: bool = False,
) -> Repo:
    """View a repo on GitHub.

    https://cli.github.com/manual/gh_repo_view

    Args:
        fields: The fields to view.
        name: The name of the repo to view.
        print_json: A flag designating whether to print the repo's field-values.

    Returns:
        An object of the GitHub repo.
    """
    args = ["gh", "repo", "view"]
    if name:
        args.append(name)
    args.append("--json=" + ",".join(fields))

    repo_str = subprocess.run(
        args,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    repo_dict = json.loads(repo_str)

    if print_json:
        print(
            Style.BRIGHT
            + "Viewing repo"
            + (f' "{name}"' if name else "")
            + "."
            + Style.RESET_ALL
        )
        print(json.dumps(repo_dict, indent=2))

    if "owner" in fields:
        repo_dict["owner"] = Repo.Owner(**repo_dict["owner"])

    return Repo(**repo_dict)


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


def fork_repo(owner: str, name: str):
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
                f"{owner}/{name}",
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
            ["gh", "repo", "clone", name, path],
            check=True,
        )
    except CalledProcessError:
        pass


def main() -> None:
    """Entry point."""
    colorama_init()

    submodules = read_submodules()

    login_to_github()

    workspace = view_repo(fields=["owner"])
    workspace_owner = t.cast(Repo.Owner, workspace.owner)

    for name, submodule in submodules.items():
        fork_repo(workspace_owner.login, name)

        clone_repo(name, submodule.path)

        view_repo(
            fields=["name", "url", "createdAt", "isFork"],
            name=name,
            print_json=True,
        )

    print(Style.BRIGHT + Fore.GREEN + "Setup completed." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
