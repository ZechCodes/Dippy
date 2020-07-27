from dippy.config.manager import ConfigManager
from typing import Any, Callable, Optional, Union
import bevy
import os
import pydantic
import pydantic.fields


def EnvField(
    env_var: str, *args, converter: Optional[Callable] = None, **kwargs
) -> Union[pydantic.fields.FieldInfo, Any]:
    """ Custom field factory that will load a value from the environment if it exists and if not it creates a Pydantic
        field.
    """
    if env_var in os.environ:
        value = os.getenv(env_var)
        if converter:
            value = converter(value)
        return value
    return pydantic.Field(*args, **kwargs)


class ConfigFactory(bevy.Factory):
    """ Custom factory for creating Pydantic models from config files. """

    def __call__(self, *file_names: str, key: Optional[str] = None) -> bevy.factory.T:
        config = self.context.get(ConfigManager).load(*file_names)
        if not config:
            config = {}

        if key:
            config = config.get(key, {})

        return self.build_type(**config)
