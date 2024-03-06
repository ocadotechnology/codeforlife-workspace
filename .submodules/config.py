"""
© Ocado Group
Created on 06/03/2024 at 10:58:17(+00:00).

Loads the configs found in config.jsonc within this directory.
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
class SubmoduleConfig:
    """A configuration for a submodule."""

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


ConfigDict = t.Dict[str, SubmoduleConfig]
InheritanceDict = t.Dict[str, t.Tuple[str, ...]]


def load_configs() -> t.Tuple[ConfigDict, InheritanceDict]:
    # Change directory to config's directory.
    os.chdir(CONFIG_DIR)

    # Load the config file.
    with open("config.jsonc", "r", encoding="utf-8") as config_file:
        json_configs = load_jsonc(config_file)

    # Convert the JSON objects to Python objects.
    assert isinstance(json_configs, dict)
    configs: ConfigDict = {}
    for key, json_config in json_configs.items():
        assert isinstance(json_config, dict)

        json_vscode = json_config.pop("vscode", None)
        if json_vscode is None:
            vscode = None
        else:
            assert isinstance(json_vscode, dict)
            vscode = VSCode(**json_vscode)  # type: ignore[arg-type]

        configs[key] = SubmoduleConfig(vscode=vscode, **json_config)  # type: ignore[arg-type]

    # Assert each submodule is specified only once.
    for submodule, count in Counter(
        [
            submodule
            for config in configs.values()
            for submodule in (config.submodules or [])
        ]
    ).items():
        assert count == 1, f"Submodule: {submodule} specified more than once."

    inheritances: InheritanceDict = {}
    for key, config in configs.items():
        inheritances[key] = _get_inheritances(config, configs)

    return configs, inheritances


def _get_inheritances(config: SubmoduleConfig, configs: ConfigDict):

    def get_inheritances(
        config: SubmoduleConfig, inheritances: t.List[str], index: int
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
                configs[inheritance],
                inheritances,
                inheritances.index(inheritance),
            )

    inheritances: t.List[str] = []

    get_inheritances(config, inheritances, index=0)

    return tuple(inheritances)
