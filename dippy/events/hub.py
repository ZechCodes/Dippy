from __future__ import annotations
from collections import defaultdict
from dippy.filters.filters import GlobalFilter
from typing import Any, Callable, Coroutine, Dict, Optional, Union


Callback = Union[Callable[[], Any], Coroutine[Any, Any, Any]]
Data = Dict[str, Any]
Filter = Callable[[Data], bool]


class EventHub:
    def __init__(self):
        self._handlers: Dict[str, Dict[Callback, EventHandler]] = defaultdict(dict)

    async def emit(
        self,
        event_name: str,
        event_data: Optional[Data] = None,
        filter_data: Optional[Data] = None,
    ):
        """Runs all handlers for an event."""
        data = event_data if event_data else {}
        for handler in self._handlers.get(event_name, {}).values():
            if handler.filter(filter_data):
                result = handler.callback(**data)
                if hasattr(result, "__await__"):
                    await result

    def off(self, event_name: str, callback: Callback):
        self._handlers.get(event_name, {}).pop(callback)

    def on(
        self,
        event_name: str,
        callback: Callback,
        predicate: Filter = GlobalFilter(),
    ) -> EventHandler:
        """Registers a callback to listen for an event. If the callack is a coroutine or returns an awaitable it'll be
        awaited."""
        handler = EventHandler(event_name, callback, predicate, self)
        self._handlers[event_name][callback] = handler
        return handler


class EventHandler:
    def __init__(
        self, event: str, callback: Callback, predicate: Filter, hub: EventHub
    ):
        self._callback = callback
        self._event = event
        self._filter = predicate
        self._stopped = False
        self._hub = hub

    @property
    def callback(self) -> Callback:
        return self._callback

    @property
    def filter(self) -> Filter:
        return self._filter

    @property
    def stopped(self) -> bool:
        return self._stopped

    def stop(self):
        self._stopped = True
        self._hub.off(self._event, self.callback)
