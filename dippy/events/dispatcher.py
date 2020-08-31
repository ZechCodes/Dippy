from __future__ import annotations
from typing import Callable, Dict, List, Union
import asyncio


class EventDispatcher:
    def __init__(self):
        self.event_listeners: Dict[List[EventHandlerCollection]] = {}


class EventHandlerCollection:
    def __init__(self):
        self.listeners: List[EventHandler] = []

    def register(self, callback: Callable) -> EventHandler:
        """ Registers a callback by wrapping it in an event handler and adding it to the handler queue. """
        handler = EventHandler(callback, self)
        self.listeners.append(handler)
        return handler

    def remove(self, callback_or_handler: Union[Callable, EventHandler]):
        """ Finds and removes a handler from the queue and cancels the handler's future. """
        index = self.listeners.index(callback_or_handler)
        if index >= 0:
            handler = self.listeners.pop(index)
            handler.cancel()

    async def run(self, *args, **kwargs):
        await asyncio.gather(
            handler.run(*args, **kwargs)
            for handler in self.listeners
            if not handler.removed()
        )


class EventHandler:
    """ Wraps a callback for an event. Attaches it to a future which can be awaited and that is refreshed each time the
    callback is run. """

    def __init__(self, callback: Callable, collection: EventHandlerCollection):
        self.callback = callback
        self.collection = collection
        self.future = asyncio.Future()

    def __await__(self):
        return self.future.__await__()

    def __eq__(self, callback_or_handler: Union[Callable, EventHandler]) -> bool:
        return self.callback == callback_or_handler or self == callback_or_handler

    def cancel(self):
        self.future.cancel()

    def remove(self):
        """ Removes the handler from the event. """
        self.collection.remove(self)

    def removed(self) -> bool:
        """ Has the handler been removed from the event. """
        return self.future.cancelled()

    async def run(self, *args, **kwargs) -> bool:
        """ Runs the callback, awaiting it if necessary, and returns True if the callback was called. If the callback
        was run the future will be marked as done and a new future will be created. """
        if self.removed():
            return False

        if asyncio.iscoroutine(self.callback):
            await self.callback(*args, **kwargs)
        else:
            self.callback(*args, **kwargs)

        # Only create a new future if the handler hasn't been marked as done, this allows the handler to be cleanly
        # removed when it's run.
        if not self.future.done():
            self.future = asyncio.Future()

        self.future.set_result(True)

        return True
