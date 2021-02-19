from __future__ import annotations
from typing import Awaitable, Callable, Dict, List, Optional
import asyncio
import inspect


class EventHub:
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self._streams: Dict[str, EventStream] = {}
        self._loop = loop

    def __getitem__(self, event_name) -> EventStream:
        if event_name not in self._streams:
            self._streams[event_name] = EventStream(self._loop)

        return self._streams[event_name]

    def emit(self, event_name: str, *args, **kwargs):
        self[event_name].push(Event(event_name, *args, **kwargs))

    def off(self, event_name: str, callback: Callable):
        self[event_name].off(callback)

    def on(self, event_name: str, callback: Callable) -> EventWatcher:
        return self[event_name].on(callback)


class EventStream:
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self._history: List[Event] = []
        self._loop = loop if loop else asyncio.get_event_loop()
        self._next = asyncio.Future(loop=self._loop)
        self._watchers: Dict[Callable, EventWatcher] = {}

    @property
    def history(self) -> List[Event]:
        return self._history

    @property
    def next(self) -> asyncio.Future:
        return self._next

    def off(self, callback: Callable):
        self._watchers[callback].off()

    def on(self, callback: Callable) -> EventWatcher:
        watcher = EventWatcher(self, callback, self._loop)
        watcher.on_stop(lambda future: self._watchers.pop(callback))
        self._watchers[callback] = watcher
        return watcher

    def push(self, event: Event):
        self._history.insert(0, event)
        self._next.set_result(event)
        self._next = asyncio.Future(loop=self._loop)


class Event:
    def __init__(self, name: str, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f"<{type(self).__name__} args={self.args}, kwargs={self.kwargs}>"


class EventWatcher:
    def __init__(
        self,
        stream: EventStream,
        callback: Callable[[Event], Optional[Awaitable]],
        loop: asyncio.AbstractEventLoop,
    ):
        self._stream = stream
        self._callback = callback
        self._future = loop.create_task(self._run())
        self._cancel = asyncio.Future()

    def off(self):
        self._future.cancel()

    def on_stop(self, callback: Callable):
        self._future.add_done_callback(callback)

    async def _run(self):
        while True:
            event = await self._stream.next
            ret = self._callback(*event.args, **event.kwargs)
            if inspect.isawaitable(ret):
                await ret
