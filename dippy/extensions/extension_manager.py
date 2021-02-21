from __future__ import annotations
from bevy import Context, Factory, Injectable
from dippy.extensions import Extension
from dippy.logging import Logging
from types import ModuleType
from typing import Dict
import importlib.util
import pathlib


class ExtensionManager(Injectable):
    context: Context
    log_factory: Factory[Logging]

    def __init__(self):
        self.log = self.log_factory("Extension Manager", level=Logging.DEBUG)
        self._extensions: Dict[str, ModuleType] = {}

    def load_extensions(self):
        path = pathlib.Path() / "extensions"
        self.log.info(f"Looking in {path.absolute()}")
        if not path.exists():
            raise FileNotFoundError(
                f"No extensions found ({path.resolve()} doesn't exist)"
            )

        if not path.is_dir():
            raise FileNotFoundError(
                f"No extensions directory found ({path.resolve()} is a file)"
            )

        for extension in path.iterdir():
            if (
                extension.suffix not in {".py", ".pyc"} and not extension.is_dir()
            ) or extension.stem.startswith("_"):
                continue  # Not detectable as a Python module/package

            try:
                self.log.debug(f"Attempting to import {extension.stem}")
                self._extensions[extension.stem] = self._import(extension)
            except ImportError:
                self.log.debug(f"Failed to import {extension.stem}")
            except Exception:
                raise ImportError(f"Failed to import {extension}")
            else:
                self.log.info(f"Loaded {extension.stem}")

    def create_extensions(self):
        for extension in Extension.__extensions__:
            logger = self.log_factory(f"{extension.__module__}.{extension.__name__}")
            logger.debug("Creating extension")
            context = self.context.branch()
            context.add(logger)
            context.add(context.create(extension))

    def _import(self, path: pathlib.Path) -> ModuleType:
        module_spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module
