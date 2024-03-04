"""
© Ocado Group
Created on 02/03/2024 at 23:46:28(+00:00).

TODO: write script description.
"""

import json
import os
import re
import subprocess
import typing as t
from collections import Counter
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path

# ------------------------------------------------------------------------------
# Global and environment variables
# ------------------------------------------------------------------------------


GIT_PUSH_CHANGES = bool(int(os.getenv("GIT_PUSH_CHANGES", "0")))
CONFIG_DIR = os.path.dirname(os.path.realpath(__file__))


# ------------------------------------------------------------------------------
# Data types and classes
# ------------------------------------------------------------------------------


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

# ------------------------------------------------------------------------------
# General helpers
# ------------------------------------------------------------------------------


def load_jsonc(file: TextIOWrapper) -> JsonValue:
    file.seek(0)
    raw_json_with_comments = file.read()
    if not raw_json_with_comments:
        return None

    # Remove single-line comments that are only preceded by white spaces.
    raw_json_without_comments = re.sub(
        r"^ *\/\/.*", "", raw_json_with_comments, flags=re.MULTILINE
    )

    return json.loads(raw_json_without_comments)


def git_commit_and_push(message: str):
    git_diff = subprocess.run(
        ["git", "diff", "--cached"], check=True, stdout=subprocess.PIPE
    ).stdout.decode("utf-8")

    if git_diff:
        subprocess.run(["git", "commit", "-m", f'"{message}"'], check=True)
        subprocess.run(["git", "push"], check=True)


# ------------------------------------------------------------------------------
# Config handlers
# ------------------------------------------------------------------------------


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
        override_value = key.startswith("!")
        keep_value = key.startswith("?")
        if override_value or keep_value:
            key = key[1:]

        if key not in json_dict:
            json_dict[key] = value
        elif keep_value:
            continue

        if value is None or isinstance(value, (str, int, bool)):
            json_dict[key] = value
        elif isinstance(value, dict):
            json_dict[key] = (
                value.copy()
                if override_value
                else merge_json_dicts(json_dict[key], value)
            )
        elif isinstance(value, list):
            json_dict[key] = (
                value.copy()
                if override_value
                else merge_json_lists(json_dict[key], value)
            )

    return json_dict


def _merge_devcontainer(devcontainer: JsonDict):
    with open(".devcontainer.json", "a+", encoding="utf-8") as devcontainer_file:
        current_devcontainer = load_jsonc(devcontainer_file)

        devcontainer = merge_json_dicts(current_devcontainer, devcontainer)

        devcontainer_file.truncate(0)
        json.dump(devcontainer, devcontainer_file, indent=2, sort_keys=True)

    if GIT_PUSH_CHANGES:
        subprocess.run(["git", "add", ".devcontainer.json"], check=True)


def merge_json_lists_of_json_objects(
    current: JsonDict,
    latest: JsonDict,
    list_names_and_obj_id_fields: t.Iterable[t.Tuple[str, str]],
):
    latest = latest.copy()

    obj_lists: t.Dict[str, t.Tuple[JsonList, JsonList]] = {}
    for list_name, _ in list_names_and_obj_id_fields:
        current_list = current.pop(list_name)
        assert isinstance(current_list, list)
        latest_list = latest.pop(list_name)
        assert isinstance(latest_list, list)

        obj_lists[list_name] = (current_list, latest_list)

    merged = merge_json_dicts(current, latest)

    for list_name, obj_id_field in list_names_and_obj_id_fields:
        current_list, latest_list = obj_lists[list_name]

        merged_list = current_list.copy()
        for obj in latest_list:
            assert isinstance(obj, dict)

            for current_obj in current_list.copy():
                assert isinstance(current_obj, dict)

                if obj[obj_id_field] == current_obj[obj_id_field]:
                    current_list.remove(current_obj)
                    merged_list.remove(current_obj)

                    obj = merge_json_dicts(current_obj, obj)
                    break

            merged_list.append(obj)

        merged[list_name] = merged_list

    return merged


def _merge_vscode_settings(settings: JsonDict):
    with open(".vscode/settings.json", "a+", encoding="utf-8") as settings_file:
        current_settings = load_jsonc(settings_file)
        if current_settings is not None:
            assert isinstance(current_settings, dict)
            settings = merge_json_dicts(current_settings, settings)

            settings_file.truncate(0)

        json.dump(settings, settings_file, indent=2, sort_keys=True)

    if GIT_PUSH_CHANGES:
        subprocess.run(["git", "add", ".vscode/settings.json"], check=True)


def _merge_vscode_tasks(tasks: JsonDict):
    with open(".vscode/tasks.json", "a+", encoding="utf-8") as tasks_file:
        current_tasks = load_jsonc(tasks_file)
        if current_tasks is not None:
            assert isinstance(current_tasks, dict)
            tasks = merge_json_lists_of_json_objects(
                current_tasks,
                tasks,
                list_names_and_obj_id_fields=[("tasks", "label")],
            )

            tasks_file.truncate(0)

        json.dump(tasks, tasks_file, indent=2, sort_keys=True)

    if GIT_PUSH_CHANGES:
        subprocess.run(["git", "add", ".vscode/tasks.json"], check=True)


def _merge_vscode_launch(launch: JsonDict):
    with open(".vscode/launch.json", "a+", encoding="utf-8") as launch_file:
        current_launch = load_jsonc(launch_file)
        if current_launch is not None:
            assert isinstance(current_launch, dict)
            launch = merge_json_lists_of_json_objects(
                current_launch,
                launch,
                list_names_and_obj_id_fields=[("configurations", "name")],
            )

            launch_file.truncate(0)

        json.dump(launch, launch_file, indent=2, sort_keys=True)

    if GIT_PUSH_CHANGES:
        subprocess.run(["git", "add", ".vscode/launch.json"], check=True)


def _merge_vscode_code_snippets(code_snippets: JsonDict):
    with open(
        ".vscode/codeforlife.code-snippets", "a+", encoding="utf-8"
    ) as code_snippets_file:
        current_code_snippets = load_jsonc(code_snippets_file)
        if current_code_snippets is not None:
            assert isinstance(current_code_snippets, dict)

            for key, code_snippet in code_snippets.items():
                current_code_snippets[key] = code_snippet
            code_snippets = current_code_snippets

            code_snippets_file.truncate(0)

        json.dump(code_snippets, code_snippets_file, indent=2, sort_keys=True)

    if GIT_PUSH_CHANGES:
        subprocess.run(
            ["git", "add", ".vscode/codeforlife.code-snippets"],
            check=True,
        )


def _merge_workspace(workspace: JsonDict):
    with open("codeforlife.code-workspace", "a+", encoding="utf-8") as workspace_file:
        current_workspace = load_jsonc(workspace_file)
        if current_workspace is not None:
            assert isinstance(current_workspace, dict)
            workspace = merge_json_lists_of_json_objects(
                current_workspace,
                workspace,
                list_names_and_obj_id_fields=[("folders", "path")],
            )

            workspace_file.truncate(0)

        json.dump(workspace, workspace_file, indent=2, sort_keys=True)

    if GIT_PUSH_CHANGES:
        subprocess.run(["git", "add", "codeforlife.code-workspace"], check=True)


def merge_config(config: SubmoduleConfig):
    if config.devcontainer:
        _merge_devcontainer(config.devcontainer)
    if config.vscode:
        # Create .vscode directory if not exists.
        Path(".vscode").mkdir(exist_ok=True)
        if config.vscode.settings:
            _merge_vscode_settings(config.vscode.settings)
        if config.vscode.tasks:
            _merge_vscode_tasks(config.vscode.tasks)
        if config.vscode.launch:
            _merge_vscode_launch(config.vscode.launch)
        if config.vscode.codeSnippets:
            _merge_vscode_code_snippets(config.vscode.codeSnippets)
    if config.workspace:
        _merge_workspace(config.workspace)


# ------------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------------


def load_configs() -> ConfigDict:
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

    return configs


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

        for inheritance in config_inheritances[::-1]:
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


def main() -> None:
    configs = load_configs()

    # Process each config.
    for key, config in configs.items():
        # Skip config if it's not going to merged into any submodules.
        if not config.submodules:
            continue

        # Print config details.
        print(f"Key: {key}")
        if config.description:
            print(f"Description: {config.description}")

        # Get and print config inheritances.
        inheritances = get_inheritances(config, configs)
        if inheritances:
            print("Inherits:")
            for inheritance in inheritances:
                inheritance_description = configs[inheritance].description
                print(
                    f"    - {inheritance}"
                    + (
                        f": {inheritance_description}"
                        if inheritance_description
                        else ""
                    )
                )

        # Print config submodules.
        print("Submodules:")
        for submodule in config.submodules:
            print(f"    - {submodule}")

        # Merge inherited configs and config into submodule in order.
        for submodule in config.submodules:
            # Change directory to submodule's directory.
            os.chdir(f"{CONFIG_DIR}/../{submodule}")

            for inheritance in inheritances:
                merge_config(configs[inheritance])

            merge_config(config)

            if GIT_PUSH_CHANGES:
                git_commit_and_push(message="Configured submodule [skip ci]")
                os.chdir(f"{CONFIG_DIR}/..")
                subprocess.run(["git", "add", submodule], check=True)

        print("---")

    if GIT_PUSH_CHANGES:
        git_commit_and_push(message="Configured submodules [skip ci]")

    print("Success!")


if __name__ == "__main__":
    main()