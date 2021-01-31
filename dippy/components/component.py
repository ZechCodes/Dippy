from dippy.components.handlers import EventHandler
from dippy.events.hub import EventHub
from dippy.logging import Logging
from dippy.filters.filters import BaseFilter, GlobalFilter
from typing import Callable, Type
import bevy


class Component(bevy.Injectable):
    events: EventHub
    logger: Logging
    handler_factory: bevy.Factory[EventHandler]

    __components__ = []
    __filters__: BaseFilter = GlobalFilter()

    def __init_subclass__(cls, **kwargs):
        Component.__components__.append(cls)

    def __init__(self, *args, **kwargs):
        self._register_event_handlers()

    def _register_event_handlers(self):
        self.logger.debug("Looking for event handlers")
        for name, attr in self.__class__.__dict__.items():
            if isinstance(attr, EventHandler):
                self.logger.debug(
                    f"Registering {attr.callback.__name__} for '{attr.event}' events"
                )
                handler = attr.bind(self)
                setattr(self, name, handler)
                self.events.on(
                    attr.event,
                    handler.callback,
                    self.__filters__ & attr.filters,
                )


def filters(
    component_filters: BaseFilter,
) -> Callable[[Type[Component]], Type[Component]]:
    def apply_filters(cls: Type[Component]) -> Type[Component]:
        cls.__filters__ = component_filters
        return cls

    return apply_filters
