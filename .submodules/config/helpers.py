"""
© Ocado Group
Created on 06/03/2024 at 11:05:06(+00:00).

General helpers.
"""

import json
import os
import re
import subprocess
import typing as t
from io import TextIOWrapper
from pathlib import Path

if t.TYPE_CHECKING:
    from configs import AnyJsonValue, JsonDict, JsonList, JsonValue

# Path to the .submodules/config directory.
CONFIG_DIR = Path(__file__).resolve().parent
# Whether or not to git-push the changes.
GIT_PUSH_CHANGES = bool(int(os.getenv("GIT_PUSH_CHANGES", "0")))


def load_jsonc(file: TextIOWrapper) -> "JsonValue":
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


def merge_json_lists(submodule_value: "JsonValue", global_list: "JsonList"):
    if not isinstance(submodule_value, list):
        return global_list

    json_list = submodule_value.copy()

    for value in global_list:
        if isinstance(value, (int, str)):
            if value not in json_list:
                json_list.append(value)
        else:
            raise NotImplementedError(
                f"Haven't implemented support for values of type {type(value)}."
            )

    return json_list


def merge_json_dicts(submodule_value: "JsonValue", global_dict: "JsonDict"):
    if not isinstance(submodule_value, dict):
        return global_dict

    json_dict = submodule_value.copy()

    for key, value in global_dict.items():
        override_submodule_value = key.startswith("!")
        keep_submodule_value = key.startswith("?")
        if override_submodule_value or keep_submodule_value:
            key = key[1:]

        if key not in json_dict:
            json_dict[key] = value
        elif keep_submodule_value:
            continue

        if value is None or isinstance(value, (str, int, bool)):
            json_dict[key] = value
        elif isinstance(value, dict):
            json_dict[key] = (
                value.copy()
                if override_submodule_value
                else merge_json_dicts(json_dict[key], value)
            )
        elif isinstance(value, list):
            json_dict[key] = (
                value.copy()
                if override_submodule_value
                else merge_json_lists(json_dict[key], value)
            )

    return json_dict


def merge_json_lists_of_json_objects(
    submodule_value: "JsonValue",
    global_dict: "JsonDict",
    list_names_and_obj_id_fields: t.Iterable[t.Tuple[str, str]],
):
    global_dict = global_dict.copy()

    if not isinstance(submodule_value, dict):
        return global_dict

    obj_lists: t.Dict[str, t.Tuple[JsonList, JsonList]] = {}
    for list_name, _ in list_names_and_obj_id_fields:
        current_list = submodule_value.pop(list_name)
        assert isinstance(current_list, list)
        latest_list = global_dict.pop(list_name)
        assert isinstance(latest_list, list)

        obj_lists[list_name] = (current_list, latest_list)

    merged_dict = merge_json_dicts(submodule_value, global_dict)

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

        merged_dict[list_name] = merged_list

    return merged_dict


def merge_submodule_file(
    file: str,
    global_value: "AnyJsonValue",
    merge: t.Callable[["JsonValue", "AnyJsonValue"], "JsonValue"],
):
    with open(file, "a+", encoding="utf-8") as submodule_file:
        submodule_value = load_jsonc(submodule_file)
        if submodule_file is None:
            value = global_value
        else:
            value = merge(submodule_value, global_value)
            submodule_file.truncate(0)

        json.dump(value, submodule_file, indent=2, sort_keys=True)

    if GIT_PUSH_CHANGES:
        subprocess.run(["git", "add", file], check=True)
