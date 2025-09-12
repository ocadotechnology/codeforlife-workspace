"""
© Ocado Group
Created on 14/04/2025 at 16:31:07(+01:00).
"""

import re
import typing as t
from dataclasses import dataclass


@dataclass(frozen=True)
class Submodule:
    """A Git submodule definition found in the file: .gitmodules."""

    path: str
    url: str


SubmoduleDict = t.Dict[str, Submodule]


def read_submodules() -> SubmoduleDict:
    """Read the submodules from .gitmodules (located at the workspace's root).

    Returns:
        A dict where the key is the name of the submodule and value is an object
        of the submodule's attributes.
    """
    with open("/workspace/.gitmodules", "r", encoding="utf-8") as gitmodules:
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
