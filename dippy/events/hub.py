from __future__ import annotations
from asyncio import iscoroutine, iscoroutinefunction
from collections import defaultdict
from typing import Any, Callable, Coroutine


class EventHub:
    def __init__(self):
        self._handlers: dict[str, set] = defaultdict(set)

    async def emit(self, event_name: str, *event_data):
        """Emits an event calling all coroutines that have been registered."""
        for handler in self._handlers.get(event_name, []):
            await handler(*event_data)

    def on(self, event_name: str, callback: Callable[[], Coroutine]):
        """Registers a coroutine to listen for an event.

        Raises ValueError if the callback is not a coroutine."""
        if not iscoroutine(callback) and not iscoroutinefunction(callback):
            raise ValueError(
                f"Event handlers must be coroutines, received a callback of type {type(callback)}"
            )

        self._handlers[event_name].add(callback)

    def stop(self, event_name: str, callback: Callable[[], Coroutine]):
        """Removes a callback from listening for an event."""
        self._handlers[event_name].remove(callback)
