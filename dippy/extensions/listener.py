from __future__ import annotations
from typing import Any, Callable
from types import MethodType


class ListenerDecorator:
    def __init__(self, event_name: str):
        self._event_name = event_name
        self._handler = None

    def __call__(self, handler: Callable[[Any, ...], Any]) -> ListenerDecorator:
        self._handler = handler
        return self

    def __get__(self, instance, owner):
        return Listener(self._event_name, MethodType(self._handler, instance))

    def __set_name__(self, owner, name):
        if hasattr(owner, "__dippy_listeners__"):
            owner.__dippy_listeners__[name] = self._event_name


class Listener:
    def __init__(self, event_name: str, handler: Callable[[Any, ...], Any]):
        self._event_name = event_name
        self._handler = handler

    @property
    def event_name(self) -> str:
        return self._event_name

    @property
    def handler(self) -> Callable[[Any, ...], Any]:
        return self._handler

    def __call__(self, *args, **kwargs):
        return self._handler(*args, **kwargs)
