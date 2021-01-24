from dippy.components import Component
from dippy.config import ConfigFactory
from dippy.logging import Logging
from types import ModuleType
from typing import List, Optional
import bevy
import enum
import importlib.util
import pathlib
import pydantic


class ComponentAutoloadPolicyEnum(enum.Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class ComponentGroupModel(pydantic.BaseModel):
    location: str
    policy: Optional[ComponentAutoloadPolicyEnum]
    components: Optional[List[str]]


class ComponentSettingsModel(pydantic.BaseModel):
    groups: List[ComponentGroupModel]
    policy: ComponentAutoloadPolicyEnum = ComponentAutoloadPolicyEnum.ENABLED


class ComponentManager(bevy.Injectable):
    config_factory: ConfigFactory[ComponentSettingsModel]
    logger_factory: bevy.Factory[Logging]
    context: bevy.Context

    def __init__(self, bot_name: str):
        self.bot_name = bot_name
        self.config = self.config_factory(key="components")
        self.logger: Logging = self.logger_factory(f"{bot_name}.components")

    def load_components(self, app_path: pathlib.Path):
        self.logger.debug("Loading components")
        if not app_path.is_dir():
            app_path = app_path.parent

        for group in self.config.groups:
            policy = self.config.policy if group.policy is None else group.policy
            location = app_path / group.location
            components = [] if group.components is None else group.components
            if not location.exists() or not location.is_dir():
                raise InvalidComponentPath(
                    f"Cannot find the component directory, '{location}'"
                    f" either does not exist or is not a valid directory"
                )

            python_files = filter(
                lambda item: item.is_file()
                and item.suffix.casefold() == ".py"
                and not item.name.startswith("_"),
                location.iterdir(),
            )
            for file in python_files:
                if (
                    file.stem in components
                    and policy == ComponentAutoloadPolicyEnum.ENABLED
                ):
                    continue
                elif (
                    file.stem not in components
                    and policy == ComponentAutoloadPolicyEnum.DISABLED
                ):
                    continue

                self.logger.debug(f"Loading {file}")
                self._import(file)

    def create_components(self):
        for component in Component.__components__:
            logger = self.logger_factory(
                f"{self.bot_name}.{component.__module__}.{component.__name__}"
            )
            logger.debug("Creating component")
            context = self.context.branch()
            context.add(logger)
            context.add(context.create(component))

    def _import(self, path: pathlib.Path) -> ModuleType:
        module_spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module


class InvalidComponentPath(Exception):
    ...
