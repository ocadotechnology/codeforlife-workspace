import typing as t
import re
import json
from dataclasses import dataclass
from io import TextIOWrapper

JsonList = t.List["JsonValue"]
JsonDict = t.Dict[str, "JsonValue"]
JsonValue = t.Union[None, int, str, bool, JsonList, JsonDict]


@dataclass(frozen=True)
class VSCode:
    """JSON files contained within the .vscode directory."""

    # The config for tasks.json.
    tasks: t.Optional[JsonDict] = None
    # The config for launch.json.
    launch: t.Optional[JsonDict] = None


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


ConfigDict = t.Dict[str, SubmoduleConfig]


def load_jsonc_file(jsonc_file: TextIOWrapper) -> JsonValue:
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
    with open(
        f"{submodule}/.devcontainer.json", "w+", encoding="utf-8"
    ) as devcontainer_file:
        current_devcontainer = load_jsonc_file(devcontainer_file)

        devcontainer = merge_json_dicts(current_devcontainer, devcontainer)

        json.dump(devcontainer, devcontainer_file, indent=2)


def merge_vscode_tasks(submodule: str, tasks: JsonDict):
    with open(f"{submodule}/.vscode/tasks.json", "w+", encoding="utf-8") as tasks_file:
        current_tasks = load_jsonc_file(tasks_file)
        assert isinstance(current_tasks, dict)

        current_task_configs = current_tasks.pop("tasks")
        assert isinstance(current_task_configs, list)
        task_configs = tasks.pop("tasks")
        assert isinstance(task_configs, list)

        tasks = merge_json_dicts(current_tasks, tasks)

        merged_task_configs = current_task_configs.copy()
        for task_config in task_configs:
            assert isinstance(task_config, dict)

            for current_task_config in current_task_configs.copy():
                assert isinstance(current_task_config, dict)

                if task_config["label"] == current_task_config["label"]:
                    current_task_configs.remove(current_task_config)
                    merged_task_configs.remove(current_task_config)
                    task_config = merge_json_dicts(current_task_config, task_config)
                    break

            merged_task_configs.append(task_config)

        tasks["tasks"] = merged_task_configs

        json.dump(tasks, tasks_file, indent=2)


def merge_vscode_launch(submodule: str, launch: JsonDict):
    with open(
        f"{submodule}/.vscode/launch.json", "w+", encoding="utf-8"
    ) as launch_file:
        current_launch = load_jsonc_file(launch_file)
        assert isinstance(current_launch, dict)

        current_launch_configs = current_launch.pop("configurations")
        assert isinstance(current_launch_configs, list)
        launch_configs = launch.pop("configurations")
        assert isinstance(launch_configs, list)

        launch = merge_json_dicts(current_launch, launch)

        merged_launch_configs = current_launch_configs.copy()
        for launch_config in launch_configs:
            assert isinstance(launch_config, dict)

            for current_launch_config in current_launch_configs.copy():
                assert isinstance(current_launch_config, dict)

                if launch_config["name"] == current_launch_config["name"]:
                    current_launch_configs.remove(current_launch_config)
                    merged_launch_configs.remove(current_launch_config)
                    task_config = merge_json_dicts(current_launch_config, launch_config)
                    break

            merged_launch_configs.append(task_config)

        launch["configurations"] = merged_launch_configs

        json.dump(launch, launch_file, indent=2)


def merge_config(submodule: str, config: SubmoduleConfig):
    if config.devcontainer:
        merge_devcontainer(submodule, config.devcontainer)
    if config.vscode:
        if config.vscode.tasks:
            merge_vscode_tasks(submodule, config.vscode.tasks)
        if config.vscode.launch:
            merge_vscode_launch(submodule, config.vscode.launch)


def main() -> None:
    # Load the config file.
    with open("submodules.config.jsonc", "r", encoding="utf-8") as config_file:
        json_configs = load_jsonc_file(config_file)

    # Convert the JSON objects to Python objects.
    assert isinstance(json_configs, dict)
    configs: ConfigDict = {}
    for key, json_config in json_configs.items():
        assert isinstance(json_config, dict)
        configs[key] = SubmoduleConfig(**json_config)  # type: ignore[arg-type]

    # Process each config.
    for key, config in configs.items():
        # Skip config if it's not going to merged into any submodules.
        if not config.submodules:
            continue

        # Print config details.
        print(f"Config: {key}")
        if config.description:
            print(f"Description: {config.description}")

        # Get and print config inheritances.
        inheritances = get_inheritances(config, configs)
        if inheritances:
            print("Inherits:")
            for inheritance in inheritances:
                print(f"    - {inheritance}")

        # Print config submodules.
        print("Submodules:")
        for submodule in config.submodules:
            print(f"    - {submodule}")

        # Merge inherited configs and config into submodule in order.
        for submodule in config.submodules:
            for inheritance in inheritances:
                merge_config(submodule, configs[inheritance])

            merge_config(submodule, config)


if __name__ == "__main__":
    main()
