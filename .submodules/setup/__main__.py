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
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from subprocess import CalledProcessError
from time import sleep

import inquirer  # type: ignore[import-untyped]
from colorama import Back, Fore, Style
from colorama import init as colorama_init

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Submodule:
    """A Git submodule definition found in the file: .gitmodules."""

    path: str
    url: str


def print_intro():
    """Prints the Code For Life logo with ascii art."""
    # short hand
    M, C, Y = Fore.MAGENTA, Fore.CYAN, Fore.YELLOW

    print(
        Style.BRIGHT
        + f"""
   {M}_____          {Y}_        ______           _      {M}_  {C}__     
  {M}/ ____|        {Y}| |      |  ____|         | |    {M}(_){C}/ _|    
 {M}| |     {C}___   {Y}__| | {M}___  {Y}| |__ {M}___  {C}_ __  {Y}| |     {M}_| {C}|_ {Y}___ 
 {M}| |    {C}/ _ \\ {Y}/ _` |{M}/ _ \\ {Y}|  __{M}/ _ \\{C}| '__| {Y}| |    {M}| |  {C}_{Y}/ _ \\
 {M}| |___{C}| (_) | {Y}(_| |  {M}__/ {Y}| | {M}| (_) {C}| |    {Y}| |____{M}| | {C}|{Y}|  __/
  {M}\\_____{C}\\___/ {Y}\\__,_|{M}\\___| {Y}|_|  {M}\\___/{C}|_|    {Y}|______{M}|_|{C}_| {Y}\\___|
"""
        + Style.RESET_ALL
        + "\nTo learn more, "
        + generate_console_link(
            "https://docs.codeforlife.education/",
            "read our documentation",
        )
        + " and "
        + generate_console_link(
            "https://www.codeforlife.education/",
            "visit our site",
        )
        + ".\n\n"
        + "👇👀👇 "
        + Style.BRIGHT
        + Back.YELLOW
        + "PLEASE READ INSTRUCTIONS"
        + Style.RESET_ALL
        + " 👇👀👇\n\n"
        + "This script will help you setup your CFL dev container by:\n"
        + " - forking each repo within our "
        + generate_console_link(
            "https://github.com/ocadotechnology/codeforlife-workspace",
            "workspace",
        )
        + " into your personal GitHub account\n"
        + " - cloning each fork from your personal GitHub account into this"
        + " container\n\n"
        + "In a moment you will be asked to log into your personal GitHub"
        + " account so that we may setup your CFL dev container as described"
        + " above. Use your keyboard to select/input your option when prompted."
        + "\n\n"
        + Style.DIM
        + "If you have any concerns about logging into your personal GitHub"
        + " account, rest assured we don't perform any malicious actions with"
        " it. You're welcome to read the source code of this script here: "
        + "/codeforlife-workspace/.submodules/setup/__main__.py.\n\n"
        + Style.RESET_ALL
        + "👆👀👆 "
        + Style.BRIGHT
        + Back.YELLOW
        + "PLEASE READ INSTRUCTIONS"
        + Style.RESET_ALL
        + " 👆👀👆\n"
    )
    input(
        "Press "
        + Style.BRIGHT
        + "Enter"
        + Style.RESET_ALL
        + " after you have read the instructions..."
    )
    print("\n")


def print_exit(error: bool):
    """Prints the exiting statement to the console.

    Args:
        error: Whether there was an error during the script-run.
    """
    print()
    print(
        "💥💣💥 "
        + Style.BRIGHT
        + Fore.RED
        + "Finished with errors."
        + Style.RESET_ALL
        + " 💥💣💥\n\n"
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
        else "✨🍰✨ "
        + Style.BRIGHT
        + Fore.GREEN
        + "Finished without errors."
        + Style.RESET_ALL
        + " ✨🍰✨\n\n"
        + "Happy coding!"
    )


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
    print(Style.BRIGHT + "Checking if you are logged into GitHub..." + Style.RESET_ALL)

    status = subprocess.run(
        ["gh", "auth", "status"],
        check=True,
        stdout=subprocess.PIPE,
    ).stdout.decode("utf-8")

    logged_in = not status.startswith("You are not logged into any GitHub hosts")

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
    print(Style.BRIGHT + "Cloning repo..." + Style.RESET_ALL)

    repo_dir = str(BASE_DIR / path)

    if os.path.isdir(repo_dir) and os.listdir(repo_dir):
        print(Style.BRIGHT + repo_dir + Style.RESET_ALL + " already exists.")

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
        print(Style.BRIGHT + Fore.YELLOW + "Failed to view repo." + Style.RESET_ALL)

        return

    repo = json.loads(repo_str)
    print(json.dumps(repo, indent=2))


def main() -> None:
    """Entry point."""
    colorama_init()

    print_intro()

    submodules = read_submodules()

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
            cloned_repo = clone_repo(name, submodule.path)

            view_repo(name)

        if not error and (not forked_repo or not cloned_repo):
            error = True

    print_exit(error)


if __name__ == "__main__":
    main()
