from typing import Any, Dict
from dippy.config.manager import ConfigLoader
import pathlib


# ###   JSON Config Loader   ### #


def _json_loader(file_path: pathlib.Path) -> Dict[str, Any]:
    import json

    with file_path.open("r") as json_file:
        return json.load(json_file)


json_loader = ConfigLoader("json", r"\.json$", _json_loader)


# ###   YAML Config Loader   ### #


def _yaml_loader(file_path: pathlib.Path) -> Dict[str, Any]:
    import yaml

    with file_path.open("r") as yaml_file:
        return yaml.safe_load(yaml_file)


yaml_loader = ConfigLoader("yaml", r"\.ya?ml$", _yaml_loader)
