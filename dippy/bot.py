from dippy.config import ConfigManager
from dippy.config.loaders import yaml_loader
from dippy.config.manager import ConfigLoader
from dippy.logging import Logging
from typing import Sequence, Type, Union
import bevy
import discord
import pathlib


class Bot:
    config_manager: ConfigManager
    logger_factory: bevy.Factory[Logging]

    def __init__(
        self,
        bot_name: str,
        status: str,
        /,
        client_class: Type[discord.Client] = discord.Client,
        **kwargs,
    ):
        self.bot_name = bot_name

        self.logger: Logging = self.logger_factory(self.bot_name)
        self.logger.setup_logger()

        self.logger.info(f"Starting bot {self.bot_name!r}")

        self.bot = self.create_bot_client(
            status=status, client_class=client_class, **kwargs
        )

    def create_bot_client(
        self, client_class: Type[discord.Client], **kwargs
    ) -> discord.Client:
        client = client_class(**kwargs)
        return client

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
        config_manager = ConfigManager(
            application_path, config_dir, config_files=config_files
        )
        for loader in loaders:
            config_manager.register_loader(loader)

        context = bevy.Context()
        context.load(config_manager)


        bot = context.create(Bot, bot_name, status)
        context.load(bot)

        return bot
