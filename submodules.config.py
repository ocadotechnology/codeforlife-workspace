import typing as t

import re
import json
from dataclasses import dataclass

JsonList = t.List["JsonValue"]
JsonDict = t.Dict[str, "JsonValue"]
JsonValue = t.Union[None, int, str, bool, JsonList, JsonDict]


@dataclass(frozen=True)
class VSCode:
    tasks: t.Optional[JsonDict] = None
    launch: t.Optional[JsonDict] = None


@dataclass(frozen=True)
class SubmoduleConfig:
    inherits: t.Optional[t.List[str]] = None
    submodules: t.Optional[t.List[str]] = None
    description: t.Optional[str] = None
    vscode: t.Optional[VSCode] = None
    devcontainer: t.Optional[JsonDict] = None


ConfigDict = t.Dict[str, SubmoduleConfig]


def load_jsonc_file(path: str) -> JsonValue:
    with open(path, "r+", encoding="utf-8") as jsonc_file:
        jsonc_file.
        raw_json_with_comments = jsonc_file.read()

    # Remove single-line comments.
    raw_json_with_comments = re.sub(
        r"^ *\/\/.*", "", raw_json_with_comments, flags=re.MULTILINE
    )

    # Remove multi-line comments.
    raw_json_without_comments = re.sub(
        r"^ *\/\*.*\*\/",
        "",
        raw_json_with_comments,
        flags=re.MULTILINE | re.DOTALL,
    )

    return json.loads(raw_json_without_comments)


def get_inheritances(config: SubmoduleConfig, configs: ConfigDict):

    def _get_inheritances(
        config: SubmoduleConfig, inheritances: t.List[str], index: int
    ):
        if not config.inherits:
            return

        config_inheritances = []
        for inheritance in config.inherits:
            if inheritance not in inheritances:
                config_inheritances.append(inheritance)

        config_inheritances.reverse()
        for inheritance in config_inheritances:
            inheritances.insert(index, inheritance)

        for inheritance in config_inheritances:
            _get_inheritances(
                configs[inheritance],
                inheritances,
                inheritances.index(inheritance),
            )

    inheritances: t.List[str] = []

    _get_inheritances(config, inheritances, index=0)

    return tuple(inheritances)


def merge_json_lists(current: JsonValue, latest: JsonList):
    if not isinstance(current, list):
        return latest

    json_list = current.copy()

    for value in latest:
        if isinstance(value, (int, str)):
            if value not in json_list:
                json_list.append(value)
        else:
            raise NotImplementedError(
                f"Haven't implemented support for values of type {type(value)}."
            )

    return json_list


def merge_json_dicts(current: JsonValue, latest: JsonDict):
    if not isinstance(current, dict):
        return latest

    json_dict = current.copy()

    for key, value in latest.items():
        if key not in json_dict or value is None or isinstance(value, (str, int, bool)):
            json_dict[key] = value
        elif isinstance(value, dict):
            json_dict[key] = merge_json_dicts(json_dict[key], value)
        elif isinstance(value, list):
            json_dict[key] = merge_json_lists(json_dict[key], value)

    return json_dict


def merge_devcontainer(submodule: str, devcontainer: JsonDict):
    devcontainer_path = f"{submodule}/.devcontainer.json"

    current_devcontainer = load_jsonc_file(devcontainer_path)
    assert isinstance(current_devcontainer, dict)

    devcontainer = merge_json_dicts(current_devcontainer, devcontainer)

    with open(devcontainer_path, "w+", encoding="utf-8") as devcontainer_file:
        json.dump(devcontainer, devcontainer_file)


def merge_vscode_tasks(submodule: str, tasks: JsonDict):
    
    current_tasks = 
    
    _tasks = tasks.pop("tasks")
    
    merge_json_dicts()
    
    for task in tasks["tasks"]


def merge_vscode_launch(submodule: str, launch: JsonDict):
    pass


def merge_config(submodule: str, config: SubmoduleConfig):
    if config.devcontainer:
        merge_devcontainer(submodule, config.devcontainer)
    if config.vscode:
        if config.vscode.tasks:
            merge_vscode_tasks(submodule, config.vscode.tasks)
        if config.vscode.launch:
            merge_vscode_launch(submodule, config.vscode.launch)


def main() -> None:
    # JSON parse the file.
    json_configs: t.Dict[str, JsonDict] = load_jsonc_file("submodules.config.jsonc")

    # Convert JSON objects to classes.
    configs = {key: SubmoduleConfig(**config) for key, config in json_configs.items()}

    for key, config in configs.items():
        if not config.submodules:
            continue

        print(f"Config: {key}")
        if config.description:
            print(f"Description: {config.description}")

        inheritances = get_inheritances(config, configs)
        if inheritances:
            print("Inherits:")
            for inheritance in inheritances:
                print(f"    - {inheritance}")

        print("Submodules:")
        for submodule in config.submodules:
            print(f"    - {submodule}")

        for submodule in config.submodules:
            for inheritance in inheritances:
                merge_config(submodule, configs[inheritance])

            merge_config(submodule, config)


if __name__ == "__main__":
    main()
