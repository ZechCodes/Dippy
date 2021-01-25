from dippy.events.hub import EventHub, EventHandler
from dippy.logging import Logging
import bevy


class Component(bevy.Injectable):
    events: EventHub
    logger: Logging

    __components__ = []

    def __init_subclass__(cls, **kwargs):
        Component.__components__.append(cls)

    def __init__(self, *args, **kwargs):
        self._register_event_handlers()

    def _register_event_handlers(self):
        self.logger.debug("Looking for event handlers")
        for attr in self.__class__.__dict__.values():
            if isinstance(attr, EventHandler):
                self.logger.debug(
                    f"Registering {attr.callback.__name__} for '{attr.event}' events"
                )
                self.events.on(attr.event, attr.bind(self))
