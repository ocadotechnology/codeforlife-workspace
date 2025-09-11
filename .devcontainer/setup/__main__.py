"""
© Ocado Group
Created on 13/05/2024 at 16:20:50(+01:00).

Setup the CFL workspace for contributors by recursively forking submodules.
"""

import sys
import typing as t

import inquirer  # type: ignore[import-untyped]
from colorama import Fore, Style
from colorama import init as colorama_init
from utils import aws, git, github, postgresql, pprint, vscode

STEP = 1
RT = t.TypeVar("RT")


def step(label: str, func: t.Callable[..., RT], *args, **kwargs) -> RT:
    """Print a label for a step and execute it.

    Args:
        label: The label to print for the step before executing it.
        func: The callback for the step.

    Returns:
        Whatever the step returns.
    """
    # pylint: disable-next=global-statement
    global STEP
    pprint.notice(f"👣 Step {STEP}: {label}.\n")
    STEP += 1
    return func(*args, **kwargs)


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
        + pprint.link(
            "https://docs.codeforlife.education/",
            "read our documentation",
        )
        + " and "
        + pprint.link(
            "https://www.codeforlife.education/",
            "visit our site",
        )
        + ".\n"
    )
    pprint.notice("Executing required steps.\n")


def print_optional_steps_instructions():
    """Prints the instructions for the optional steps."""
    answers = inquirer.prompt(
        [
            inquirer.Confirm(
                "run",
                message="Would you like to run the optional steps? (recommended)",
            )
        ]
    )

    if answers and not t.cast(bool, answers["run"]):
        sys.exit()

    # TODO: Create process as numbered list where user can decide how far in the
    # process they would like to go. For example:
    # "-1": Exit. Do nothing.
    # "0": Run all steps below.
    # "1": Log into GitHub.
    # "2": Fork and clone each repo in the workspace.
    pprint.warn("👇👀👇 PLEASE READ INSTRUCTIONS 👇👀👇")
    print(
        "\nThis script will help you set up your CFL dev container by:\n"
        + " - forking each repo within our "
        + pprint.link(
            "https://github.com/ocadotechnology/codeforlife-workspace",
            "workspace",
        )
        + " into your personal GitHub account\n"
        + " - cloning each fork from your personal GitHub account into this"
        + " container\n\n"
        + "In a moment you will be asked to log into your personal GitHub"
        + " account so that we may set up your CFL dev container as described"
        + " above. Use your keyboard to select/input your option when prompted."
        + "\n"
    )
    pprint.note(
        "If you have any concerns about logging into your personal GitHub"
        + " account, rest assured we don't perform any malicious actions with"
        " it. You're welcome to read the source code of this script here: "
        + "/workspace/.devcontainer/setup/__main__.py.\n"
    )
    pprint.warn("👆👀👆 PLEASE READ INSTRUCTIONS 👆👀👆")
    input(
        "\nPress "
        + Style.BRIGHT
        + "Enter"
        + Style.RESET_ALL
        + " after you have read the instructions..."
    )
    print()


def print_exit(error: bool):
    """Prints the exiting statement to the console.

    Args:
        error: Whether there was an error during the script-run.
    """
    print()
    if error:
        pprint.error("💥💣💥 Finished with errors. 💥💣💥")
        print(
            "\nThis may not be an issue and may be occurring because you've run"
            + " this setup script before. Please read the above logs to"
            + " discover if further action is required."
        )
        print(
            "\nIf you require help, please reach out to "
            + pprint.link(
                "mailto:codeforlife@ocado.com",
                "codeforlife@ocado.com",
            )
            + "."
        )
    else:
        pprint.success("✨🍰✨ Finished without errors. ✨🍰✨")
        print("\nHappy coding!")
    print()


def main() -> None:
    """Entry point."""
    colorama_init()

    print_intro()

    submodules = step("Reading Git Submodules", git.read_submodules)

    code_workspace = step("Loading Code Workspace", vscode.load_code_workspace)

    # TODO: step(for each submodule, auto-install dependencies)

    # TODO: load connections from each BE service's settings.
    db_error = step(
        "Creating PostgreSQL resources",
        postgresql.create_resources,
        code_workspace,
    )

    # TODO: load queues from each BE service's settings.
    queue_error = step(
        "Creating AWS resources",
        aws.create_resources,
        sqs_queue_names={"portal", "contributor", "template"},
    )

    print_optional_steps_instructions()

    step("Login to GitHub", github.login)

    repo_error = step(
        "Fork and clone each repo from GitHub",
        github.fork_and_clone_repos,
        submodules,
    )

    print_exit(error=any([db_error, queue_error, repo_error]))


if __name__ == "__main__":
    main()
