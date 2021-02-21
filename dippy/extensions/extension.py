from __future__ import annotations
from bevy import Injectable
from dippy.extensions.listener import ListenerDecorator
from dippy.events import EventHub
from typing import Dict, List, Type


class Extension(Injectable):
    events: EventHub

    __dippy_listeners__: Dict[str, str] = {}
    __extensions__: List[Type[Extension]] = []

    def __init_subclass__(cls, **kwargs):
        cls.__extensions__.append(cls)

    def __init__(self):
        for handler_name, event_name in self.__dippy_listeners__.items():
            self.events.on(event_name, getattr(self, handler_name))

    @classmethod
    def listener(cls, event_name: str) -> ListenerDecorator:
        return ListenerDecorator(event_name)
