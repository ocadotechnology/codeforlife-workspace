"""
© Ocado Group
Created on 06/03/2024 at 10:58:17(+00:00).

Loads the global submodule-configs found in .submodules/configs.jsonc.
"""

import os
import typing as t
from collections import Counter
from dataclasses import dataclass

from helpers import CONFIG_DIR, load_jsonc

# JSON type hints.
JsonList = t.List["JsonValue"]
JsonDict = t.Dict[str, "JsonValue"]
JsonValue = t.Union[None, int, str, bool, JsonList, JsonDict]

AnyJsonValue = t.TypeVar("AnyJsonValue", bound=JsonValue)


@dataclass(frozen=True)
class VSCode:
    """JSON files contained within the .vscode directory."""

    # The config for settings.json.
    settings: t.Optional[JsonDict] = None
    # The config for tasks.json.
    tasks: t.Optional[JsonDict] = None
    # The config for launch.json.
    launch: t.Optional[JsonDict] = None
    # The config for codeforlife.code-snippets.
    codeSnippets: t.Optional[JsonDict] = None


@dataclass(frozen=True)
class GlobalSubmoduleConfig:
    """
    A global configuration to be applied to a number of submodules or inherited
    by other global configurations.
    """

    # The configs this config inherits.
    inherits: t.Optional[t.List[str]] = None
    # The submodules this config should be merged into.
    submodules: t.Optional[t.List[str]] = None
    # A description of this config's target.
    description: t.Optional[str] = None
    # The VSCode config files to merge with.
    vscode: t.Optional[VSCode] = None
    # The devcontainer config.
    devcontainer: t.Optional[JsonDict] = None
    # The workspace config.
    workspace: t.Optional[JsonDict] = None


GlobalConfigDict = t.Dict[str, GlobalSubmoduleConfig]
InheritanceDict = t.Dict[str, t.Tuple[str, ...]]


def load_global_configs() -> t.Tuple[GlobalConfigDict, InheritanceDict]:
    # Change directory to .submodules.
    os.chdir(CONFIG_DIR)

    # Load the configs file.
    with open("configs.jsonc", "r", encoding="utf-8") as configs_file:
        global_json_configs = load_jsonc(configs_file)

    assert isinstance(global_json_configs, dict)

    # Convert the JSON objects to Python objects.
    global_configs: GlobalConfigDict = {}
    for key, global_json_config in global_json_configs.items():
        assert isinstance(global_json_config, dict)

        json_vscode = global_json_config.pop("vscode", None)
        if json_vscode is None:
            vscode = None
        else:
            assert isinstance(json_vscode, dict)
            vscode = VSCode(**json_vscode)  # type: ignore[arg-type]

        global_configs[key] = GlobalSubmoduleConfig(
            vscode=vscode,
            **global_json_config,  # type: ignore[arg-type]
        )

    # Assert each submodule is specified only once.
    for submodule, count in Counter(
        [
            submodule
            for global_config in global_configs.values()
            for submodule in (global_config.submodules or [])
        ]
    ).items():
        assert count == 1, f"Submodule: {submodule} specified more than once."

    inheritances: InheritanceDict = {}
    for key, global_config in global_configs.items():
        inheritances[key] = _get_inheritances(global_config, global_configs)

    return global_configs, inheritances


def _get_inheritances(
    global_config: GlobalSubmoduleConfig,
    global_configs: GlobalConfigDict,
):

    def get_inheritances(
        config: GlobalSubmoduleConfig, inheritances: t.List[str], index: int
    ):
        if not config.inherits:
            return

        config_inheritances = []
        for inheritance in config.inherits:
            if inheritance not in inheritances:
                config_inheritances.append(inheritance)

        for inheritance in config_inheritances[::-1]:
            inheritances.insert(index, inheritance)

        for inheritance in config_inheritances:
            get_inheritances(
                global_configs[inheritance],
                inheritances,
                inheritances.index(inheritance),
            )

    inheritances: t.List[str] = []

    get_inheritances(global_config, inheritances, index=0)

    return tuple(inheritances)
