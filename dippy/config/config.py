from typing import Any, Optional
import dippy.config.manager as manager
import os


class Config:
    manager: manager.ConfigManager

    def __init__(self, *file_names: str):
        self.config = self.manager.load(*file_names)

    def get_value(
            self,
            /,
            name: str,
            *,
            default: Optional[Any] = None,
            env_name: Optional[str] = None,
            required: bool = False
    ) -> Any:
        """ Gets a value from the config. If it is not found it can fall back to an environment variable. """
        if name in self.config:
            return self.config[name]

        if env_name and env_name in os.environ:
            return os.getenv(env_name)

        if required:
            raise RequiredValueNotFound(f"The required value '{name}' was not found in the loaded config")

        return default


class RequiredValueNotFound(Exception):
    ...
