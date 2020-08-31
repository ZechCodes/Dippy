from dippy.components import ComponentManager
from dippy.config import ConfigManager
from dippy.config.loaders import yaml_loader
from dippy.config.manager import ConfigLoader
from dippy.events import EventClient
from dippy.logging import Logging
from typing import Sequence, Union
import bevy
import pathlib


class Bot:
    component_manager: ComponentManager
    config_manager: ConfigManager
    logger_factory: bevy.Factory[Logging]

    def __init__(
        self,
        bot_name: str,
        status: str,
        /,
        application_path: Union[pathlib.Path, str],
        **kwargs,
    ):
        self.bot_name = bot_name

        self.logger: Logging = self.logger_factory(self.bot_name)
        self.logger.setup_logger()

        self.logger.info(f"Starting bot {self.bot_name!r}")

        self.component_manager.load_components(pathlib.Path(application_path))
        self.component_manager.create_components()

        self.bot = self.create_bot_client(status=status, **kwargs)

    def create_bot_client(self, **kwargs) -> EventClient:
        return EventClient(**kwargs)

    def run(self, token: str):
        self.bot.run(token)

    @classmethod
    def create(
        cls,
        bot_name: str,
        status: str,
        application_path: Union[pathlib.Path, str],
        /,
        *,
        config_dir: str = "config",
        config_files: Sequence[str] = ("development.yaml", "production.yaml"),
        loaders: Sequence[ConfigLoader] = (yaml_loader,),
    ) -> "Bot":
        context = bevy.Context()
        context.load(
            ConfigManager(
                application_path,
                config_dir,
                config_files=config_files,
                config_loaders=loaders,
            )
        )
        context.load(context.create(ComponentManager, bot_name))

        bot = context.create(Bot, bot_name, status, application_path)
        context.load(bot)

        return bot
