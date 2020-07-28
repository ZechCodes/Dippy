from __future__ import annotations
from typing import Any, Callable, Dict, Sequence, Union
import functools
import pathlib
import re


class ConfigLoader:
    def __init__(
        self,
        name: str,
        regex: Union[re.Pattern, str],
        loader: Callable[[pathlib.Path], Any],
    ):
        self.loader = loader
        self.name = name
        self.pattern: re.Pattern = regex if isinstance(
            regex, re.Pattern
        ) else re.compile(regex, re.IGNORECASE)

    def load(self, file_path: pathlib.Path) -> Any:
        """ Call the loader with the given file path. """
        return self.loader(file_path)

    def matches(self, file_name: str) -> bool:
        """ Determine if the loader's pattern matches the given file name. """
        return self.pattern.search(file_name) is not None


class ConfigManager:
    """ Configuration File Management

        Provides basic functionality for resolving which config file to use, finding the appropriate loader interface,
        and caching config files once loaded.

        When initializing it is necessary to pass in an app path which should be the __file__ attribute of the module
        that should be considered the root of the project. Config will then use the parent directory from that path as
        the project root. It also takes a config path which should be path relative to the project root that goes to the
        directory that should contain all config files.
    """

    def __init__(
        self,
        app_path: str,
        relative_config_path: str = "",
        config_files: Sequence[str] = tuple(),
        config_loaders: Sequence[ConfigLoader] = tuple(),
    ):
        self.cache: Dict[str:Any] = {}
        self.config_path = self.get_validated_path(app_path, relative_config_path)
        self.loaders: Dict[str, ConfigLoader] = {}
        self.default_config_files = config_files

        for loader in config_loaders:
            self.register_loader(loader)

    def load(self, *config_file_names: str) -> Any:
        """ Loads a config file using the appropriate config file loader. """
        config_file_name = self.resolve_config_file(
            config_file_names if config_file_names else self.default_config_files
        )
        file_path = self.get_validated_config_path(config_file_name)
        loader = self.get_loader(config_file_name)
        return loader.load(file_path)

    def get_loader(self, file_name: str) -> ConfigLoader:
        """ Finds a loader that can handle the requested config file. """
        for loader in self.loaders.values():
            if loader.matches(file_name):
                return loader
        else:
            raise NoConfigLoaderFound(
                f"No registered config loader matched the requested file: '{file_name}'"
            )

    def get_validated_config_path(self, file_name: str) -> pathlib.Path:
        """ Builds a config file path and ensures it exists and is a file. """
        path = self.config_path / file_name
        if not path.exists() or not path.is_file():
            raise InvalidConfigPath(
                f"Cannot find the requested config file, '{path}' either does not exist or is not a valid file"
            )

        return path

    def get_validated_path(
        self, app_path: str, relative_config_path: str
    ) -> pathlib.Path:
        """ Builds the config directory path and ensures it exists and is a directory. """
        path = pathlib.Path(app_path)
        if path.is_file():
            path = path.parent

        if relative_config_path:
            path = path / relative_config_path

        if not path.exists() or not path.is_dir():
            raise InvalidConfigPath(
                f"Cannot find the config directory, '{path}' either does not exist or is not a valid directory"
            )

        return path

    @functools.singledispatchmethod
    def register_loader(
        self, name: str, regex: Union[str, re.Pattern], loader: Callable
    ):
        """ Creates and registers a config loader with the config manager. """
        self.loaders[name] = ConfigLoader(name, regex, loader)

    @register_loader.register
    def _(self, config_loader: ConfigLoader):
        """ Registers a config loader with the config manager. """
        self.loaders[config_loader.name] = config_loader

    def resolve_config_file(self, config_files: Sequence[str]) -> str:
        """ Finds the first config file that exists. """
        for config_file in config_files:
            try:
                self.get_validated_config_path(config_file)
            except InvalidConfigPath:
                pass
            else:
                return config_file
        raise InvalidConfigPath(
            f"Cannot find any of the requested config files, they either do not exist or are not valid files\n"
            f"--- Looked in {str(self.config_path)!r} for {', '.join(map(repr, config_files))}"
        )


class InvalidConfigPath(Exception):
    ...


class NoConfigLoaderFound(Exception):
    ...
