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

if t.TYPE_CHECKING:
    from config import JsonDict, JsonList, JsonValue

# Path to the .submodules directory.
CONFIG_DIR = os.path.dirname(os.path.realpath(__file__))


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


def merge_json_lists(current: "JsonValue", latest: "JsonList"):
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


def merge_json_dicts(current: "JsonValue", latest: "JsonDict"):
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


def merge_json_lists_of_json_objects(
    current: "JsonDict",
    latest: "JsonDict",
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
