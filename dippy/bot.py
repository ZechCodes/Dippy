from dippy.components import ComponentManager
from dippy.config import ConfigManager
from dippy.config.loaders import yaml_loader
from dippy.config.manager import ConfigLoader
from dippy.events import EventHub
from dippy.logging import Logging
from typing import Callable, Optional, Sequence, Type, Union
import bevy
import discord
import pathlib


class Bot(bevy.Injectable):
    component_manager: ComponentManager
    config_manager: ConfigManager
    logger_factory: bevy.Factory[Logging]
    events: EventHub
    client: discord.Client

    def __init__(self, bot_name: str, application_path: Union[pathlib.Path, str], /):
        self.bot_name = bot_name
        self.path = self._tidy_app_path(application_path)

        self.logger: Logging = self.logger_factory(self.bot_name)
        self.logger.setup_logger()

        self.logger.info(
            f"Starting bot\n"
            f"  Name: {self.bot_name!r}\n"
            f"  Path: {self.path.resolve()} ({'EXISTS' if self.path.exists() else 'DOES NOT EXIST'})\n"
        )

        self.component_manager.load_components(pathlib.Path(application_path))
        self.component_manager.create_components()

        self._setup_event_forwarding()

    def run(self, token: str):
        self.client.run(token)

    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            await self.events.emit(
                "direct_message", message, message.channel, message.channel.recipient
            )
        else:
            await self.events.emit(
                "message", message, message.channel, message.channel.guild
            )

    def _setup_event_forwarding(self):
        # Try to use the listen method if possible, otherwise fallback to using event
        # listen is preferred as it won't override any existing event handlers defined on the client
        register: Callable[[Callable], None] = (
            self.client.listen()
            if hasattr(self.client, "listen")
            else self.client.event
        )
        register(self.on_message)

    def _tidy_app_path(self, path: Union[pathlib.Path, str]) -> pathlib.Path:
        tidy_path = pathlib.Path(path)
        return tidy_path if tidy_path.is_dir() else tidy_path.parent

    @classmethod
    def create(
        cls,
        bot_name: str,
        application_path: Union[pathlib.Path, str],
        /,
        *,
        client: Optional[Type[discord.Client]] = None,
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

        context.add((client if client else discord.Client)(**client_options))

        bot = context.create(cls, bot_name, application_path)
        context.add(bot)

        return bot
