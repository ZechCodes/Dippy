from dippy.components import ComponentManager
from dippy.config import ConfigManager
from dippy.config.loaders import yaml_loader
from dippy.config.manager import ConfigLoader
from dippy.events import EventHub
from dippy.logging import Logging
from typing import Optional, Sequence, Union
import bevy
import discord
import pathlib


class Bot(bevy.Injectable):
    component_manager: ComponentManager
    config_manager: ConfigManager
    logger_factory: bevy.Factory[Logging]
    events: EventHub
    client: discord.Client

    def __init__(
        self,
        bot_name: str,
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

    def run(self, token: str):
        self.client.run(token)

    @classmethod
    def create(
        cls,
        bot_name: str,
        application_path: Union[pathlib.Path, str],
        /,
        *,
        client: Optional[discord.Client] = None,
        config_dir: str = "config",
        config_files: Sequence[str] = ("development.yaml", "production.yaml"),
        loaders: Sequence[ConfigLoader] = (yaml_loader,),
        **client_options,
    ) -> "Bot":
        context = bevy.Context()
        context.add(
            ConfigManager(
                application_path,
                config_dir,
                config_files=config_files,
                config_loaders=loaders,
            )
        )
        context.add(context.create(ComponentManager, bot_name))

        context.add(discord.Client(**client_options))

        bot = context.create(cls, bot_name, application_path)
        context.add(bot)

        return bot
