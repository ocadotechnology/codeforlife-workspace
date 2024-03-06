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

import os
import subprocess
from pathlib import Path

from configs import GlobalSubmoduleConfig, JsonDict, JsonValue, load_global_configs
from helpers import (
    DOT_SUBMODULES_DIR,
    GIT_PUSH_CHANGES,
    git_commit_and_push,
    merge_json_dicts,
    merge_json_lists_of_json_objects,
    merge_submodule_file,
)


def _merge_vscode_code_snippets(global_code_snippets: JsonDict):
    def merge(
        submodule_code_snippets: JsonValue,
        global_code_snippets: JsonDict,
    ):
        assert isinstance(submodule_code_snippets, dict)

        for key, code_snippet in global_code_snippets.items():
            submodule_code_snippets[key] = code_snippet

        return submodule_code_snippets

    merge_submodule_file(
        ".vscode/codeforlife.code-snippets",
        global_code_snippets,
        merge,
    )


def merge_global_config(global_config: GlobalSubmoduleConfig):
    if global_config.devcontainer:
        merge_submodule_file(
            ".devcontainer.json",
            global_config.devcontainer,
            merge_json_dicts,
        )

    if global_config.vscode:
        # Create .vscode directory if not exists.
        Path(".vscode").mkdir(exist_ok=True)

        if global_config.vscode.settings:
            merge_submodule_file(
                ".vscode/settings.json",
                global_config.vscode.settings,
                merge_json_dicts,
            )

        if global_config.vscode.tasks:
            merge_submodule_file(
                ".vscode/tasks.json",
                global_config.vscode.tasks,
                merge=lambda submodule_tasks, global_tasks: (
                    merge_json_lists_of_json_objects(
                        submodule_tasks,
                        global_tasks,
                        list_names_and_obj_id_fields=[("tasks", "label")],
                    )
                ),
            )

        if global_config.vscode.launch:
            merge_submodule_file(
                ".vscode/launch.json",
                global_config.vscode.launch,
                merge=lambda submodule_launch, global_launch: (
                    merge_json_lists_of_json_objects(
                        submodule_launch,
                        global_launch,
                        list_names_and_obj_id_fields=[("configurations", "name")],
                    )
                ),
            )

        if global_config.vscode.codeSnippets:
            _merge_vscode_code_snippets(global_config.vscode.codeSnippets)

    if global_config.workspace:
        merge_submodule_file(
            "codeforlife.code-workspace",
            global_config.workspace,
            merge=lambda submodule_workspace, global_workspace: (
                merge_json_lists_of_json_objects(
                    submodule_workspace,
                    global_workspace,
                    list_names_and_obj_id_fields=[("folders", "path")],
                )
            ),
        )


def main() -> None:
    global_configs, inheritances = load_global_configs()

    # Process each config.
    for key, global_config in global_configs.items():
        # Skip config if it's not going to merged into any submodules.
        if not global_config.submodules:
            continue

        # Print config details.
        print(f"Key: {key}")
        if global_config.description:
            print(f"Description: {global_config.description}")

        # Print config inheritances.
        if inheritances[key]:
            print("Inherits:")
            for inheritance in inheritances[key]:
                inheritance_description = global_configs[inheritance].description
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
        for submodule in global_config.submodules:
            print(f"    - {submodule}")

        # Merge inherited configs and config into submodule in order.
        for submodule in global_config.submodules:
            # Change directory to submodule's directory.
            os.chdir(f"{DOT_SUBMODULES_DIR}/../{submodule}")

            for inheritance in inheritances[key]:
                merge_global_config(global_configs[inheritance])

            merge_global_config(global_config)

            if GIT_PUSH_CHANGES:
                git_commit_and_push(message="Configured submodule [skip ci]")
                os.chdir(f"{DOT_SUBMODULES_DIR}/..")
                subprocess.run(["git", "add", submodule], check=True)

        print("---")

    if GIT_PUSH_CHANGES:
        git_commit_and_push(message="Configured submodules [skip ci]")

    print("Success!")


if __name__ == "__main__":
    main()
