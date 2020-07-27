from typing import Any, Dict
import pathlib


def json_loader(file_path: pathlib.Path) -> Dict[str, Any]:
    import json

    with file_path.open("r") as json_file:
        return json.load(json_file)

