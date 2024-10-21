"""
© Ocado Group
Created on 13/05/2024 at 16:20:50(+01:00).

Setup the CFL workspace for contributors by recursively forking submodules.
"""

import json
import os
import re
import subprocess
import typing as t
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from subprocess import CalledProcessError
from time import sleep

from colorama import Back, Fore, Style
from colorama import init as colorama_init

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Submodule:
    """A Git submodule definition found in the file: .gitmodules."""

    path: str
    url: str


def generate_console_link(
    url: str,
    label: t.Optional[str] = None,
    parameters: str = "",
):
    """Generates a link to be printed in the console.

    Args:
        url: The link to follow.
        label: The label of the link. If not given, the url will be the label.
        parameters: Any url parameters you may have.

    Returns:
        A link that can be clicked in the console.
    """
    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST
    return f"\033]8;{parameters};{url}\033\\{label or url}\033]8;;\033\\"


def get_namespace() -> Namespace:
    """Get the command line values passed to this script.

    Returns:
        An object containing all the command line values.
    """
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--skip-login",
        action="store_true",
        dest="skip_login",
        default=False,
        help="Skip login if already logged in.",
    )
    arg_parser.add_argument(
        "--overwrite-clone",
        action="store_true",
        dest="overwrite_clone",
        default=False,
        help=(
            "Deletes each clone's current directory if they have one and clones"
            " each repo."
        ),
    )

    return arg_parser.parse_args()


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
        r'^\[submodule "(.*)"\]$',
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


def fork_repo(url: str):
    """Fork a repo on GitHub.

    https://cli.github.com/manual/gh_repo_fork

    Args:
        owner: The owner of the repo to fork.
        name: The name of the repo to fork.

    Returns:
        A flag designating whether the repo was successfully forked.
    """
    print(Style.BRIGHT + "Forking repo..." + Style.RESET_ALL)

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
        print(Style.BRIGHT + Fore.RED + "Failed to fork repo." + Style.RESET_ALL)

        return False

    return True


def clone_repo(name: str, path: str, overwrite: bool):
    # pylint: disable=line-too-long
    """Clone a repo from GitHub.

    https://cli.github.com/manual/gh_repo_clone

    Args:
        name: The name of the repo to clone.
        path: The paths to clone the repo to.
        overwrite: A flag designating whether to delete the repo's current directory if it exists and clone the repo in the directory.

    Returns:
        A flag designating whether the repo was successfully cloned.
    """
    # pylint: enable=line-too-long
    print(Style.BRIGHT + "Cloning repo..." + Style.RESET_ALL)

    repo_dir = str(BASE_DIR / path)

    if os.path.isdir(repo_dir) and os.listdir(repo_dir):
        print(Style.BRIGHT + repo_dir + Style.RESET_ALL + " already exists.")

        if overwrite:
            rmtree(repo_dir)
        else:
            return True

    retry_delay, max_retries = 1, 5
    for retry_index in range(max_retries):
        try:
            subprocess.run(
                ["gh", "repo", "clone", name, repo_dir],
                check=True,
            )

            return True
        except CalledProcessError:
            if os.path.isdir(repo_dir):
                rmtree(repo_dir)

            print(
                Style.BRIGHT
                + Fore.YELLOW
                + f"Retrying clone in {retry_delay} seconds."
                + f" Attempt {retry_index + 1}/{max_retries}."
                + Style.RESET_ALL
            )

            sleep(retry_delay)
            retry_delay *= 2

    print(Style.BRIGHT + Fore.RED + "Failed to clone repo." + Style.RESET_ALL)

    return False


def view_repo(name: str):
    """Print a repo on GitHub as a JSON object.

    https://cli.github.com/manual/gh_repo_view

    Args:
        name: The name of the repo to view.
    """
    print(Style.BRIGHT + "Viewing repo..." + Style.RESET_ALL)

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
        print(Fore.YELLOW + "Failed to view repo." + Style.RESET_ALL)

        return

    repo = json.loads(repo_str)
    print(json.dumps(repo, indent=2))


def main() -> None:
    """Entry point."""
    colorama_init()

    namespace = get_namespace()

    submodules = read_submodules()

    if not namespace.skip_login:
        login_to_github()

    error = False

    for i, (name, submodule) in enumerate(submodules.items(), start=1):
        print(
            Style.DIM
            + Back.GREEN
            + f"Submodule ({i}/{len(submodules)}): {name}"
            + Style.RESET_ALL
        )

        forked_repo = fork_repo(submodule.url)

        cloned_repo = False
        if forked_repo:
            cloned_repo = clone_repo(
                name,
                submodule.path,
                namespace.overwrite_clone,
            )

            view_repo(name)

        if not error and (not forked_repo or not cloned_repo):
            error = True

    print()
    print(
        Style.BRIGHT
        + Fore.RED
        + "💥💣💥 Finished with errors. 💥💣💥"
        + Style.RESET_ALL
        + "\n\n"
        + "This may not be an issue and may be occurring because you've run"
        + " this setup script before. Please read the above logs to discover if"
        + " further action is required."
        + "\n\n"
        + "If you require help, please reach out to "
        + generate_console_link(
            "mailto:codeforlife@ocado.com",
            "codeforlife@ocado.com",
        )
        + "."
        if error
        else Style.BRIGHT
        + Fore.GREEN
        + "✨🍰✨ Finished without errors. ✨🍰✨"
        + Style.RESET_ALL
        + "\n\n"
        + "Happy coding!"
    )


if __name__ == "__main__":
    main()
