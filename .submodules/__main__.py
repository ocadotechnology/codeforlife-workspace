"""
© Ocado Group
Created on 02/03/2024 at 23:46:28(+00:00).

This file is used to configure CFL's submodules using the global-config defined
in the config.jsonc file in this directory.

By default, the global-config is *merged* into any existing config within each
submodule. That is, any values defined in the global-config will override the
values found in a submodule's config but if a submodule has key:value pairs not
present in the global-config, they will remain. However, in some cases, the
behavior is to override the values (values not present in the global-config will
be removed).
"""

import json
import os
import subprocess
from pathlib import Path

from config import JsonDict, SubmoduleConfig, load_configs
from helpers import (
    CONFIG_DIR,
    git_commit_and_push,
    load_jsonc,
    merge_json_dicts,
    merge_json_lists_of_json_objects,
)

GIT_PUSH_CHANGES = bool(int(os.getenv("GIT_PUSH_CHANGES", "0")))


def _merge_devcontainer(devcontainer: JsonDict):
    with open(".devcontainer.json", "a+", encoding="utf-8") as devcontainer_file:
        current_devcontainer = load_jsonc(devcontainer_file)

        devcontainer = merge_json_dicts(current_devcontainer, devcontainer)

        devcontainer_file.truncate(0)
        json.dump(devcontainer, devcontainer_file, indent=2, sort_keys=True)

    if GIT_PUSH_CHANGES:
        subprocess.run(["git", "add", ".devcontainer.json"], check=True)


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


def main() -> None:
    configs, inheritances = load_configs()

    # Process each config.
    for key, config in configs.items():
        # Skip config if it's not going to merged into any submodules.
        if not config.submodules:
            continue

        # Print config details.
        print(f"Key: {key}")
        if config.description:
            print(f"Description: {config.description}")

        # Print config inheritances.
        if inheritances[key]:
            print("Inherits:")
            for inheritance in inheritances[key]:
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

            for inheritance in inheritances[key]:
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
