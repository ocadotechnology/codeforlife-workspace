"""
© Ocado Group
Created on 15/04/2025 at 14:57:23(+01:00).

Pretty print utilities.
"""

import typing as t

from colorama import Back, Fore, Style


def link(
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


def header(text: str):
    """Print a stylized header.

    Args:
        text: The text to print.
    """
    print(Style.DIM + Back.GREEN + text + Style.RESET_ALL)


def warn(text: str):
    """Print a stylized warning.

    Args:
        text: The text to print.
    """
    print(Style.BRIGHT + Fore.YELLOW + text + Style.RESET_ALL)


def error(text: str):
    """Print a stylized error.

    Args:
        text: The text to print.
    """
    print(Style.BRIGHT + Fore.RED + text + Style.RESET_ALL)


def notice(text: str):
    """Print a stylized notice.

    Args:
        text: The text to print.
    """
    print(Style.BRIGHT + text + Style.RESET_ALL)


def success(text: str):
    """Print a stylized success.

    Args:
        text: The text to print.
    """
    print(Style.BRIGHT + Fore.GREEN + text + Style.RESET_ALL)


def note(text: str):
    """Print a stylized note.

    Args:
        text: The text to print.
    """
    print(Style.DIM + text + Style.RESET_ALL)
