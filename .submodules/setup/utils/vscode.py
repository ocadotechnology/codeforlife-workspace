"""
© Ocado Group
Created on 14/04/2025 at 16:23:22(+01:00).
"""

import json
import re
import typing as t

from .settings import WORKSPACE_DIR


class Folder(t.TypedDict):
    """A code workspace folder."""

    path: str
    name: t.NotRequired[str]


class CodeWorkspace(t.TypedDict):
    """
    The code workspace definition found in the file: codeforlife.code-workspace.
    """

    folders: t.List[Folder]
    settings: t.Dict[str, t.Any]


def load_code_workspace() -> CodeWorkspace:
    """Load the .code-workspace file.

    Returns:
        A JSON dict containing the code workspace.
    """
    with open(
        WORKSPACE_DIR / "codeforlife.code-workspace",
        "r",
        encoding="utf-8",
    ) as code_workspace:
        code_workspace_str = code_workspace.read()

    code_workspace_str = re.sub(r"//.*", "", code_workspace_str)

    return json.loads(code_workspace_str)
