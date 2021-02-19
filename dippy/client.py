from bevy import Factory, Injectable
from dippy.events import EventHub
from dippy.extensions.extension import ExtensionManager
from dippy.logging import Logging
from discord.ext.commands import Bot


class Client(Bot, Injectable):
    log_factory: Factory[Logging]
    events: EventHub
    extension_manager: ExtensionManager

    def __init__(self, name: str = "Dippy.bot", *args, **kwargs):
        super().__init__(*args, **kwargs)
        Logging.setup_logger()

        self.log = self.log_factory(name)
        self.extension_manager.load_extensions()
        self.extension_manager.create_extensions()

    def dispatch(self, event_name, *args, **kwargs):
        super(Client, self).dispatch(event_name, *args, **kwargs)
        self.events.emit(event_name, *args, *kwargs)

    async def on_ready(self):
        self.log.info("Bot is ready")

    @classmethod
    def launch(cls, token: str = None, *args, **kwargs):
        client = cls(*args, **kwargs)
        client.run(token)
