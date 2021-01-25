from __future__ import annotations
from asyncio import iscoroutine, iscoroutinefunction
from collections import defaultdict
from types import MethodType
from typing import Any, Callable, Coroutine, Dict, List, Tuple


class EventHub:
    def __init__(self):
        self._handlers: dict[str, set] = defaultdict(set)

    async def emit(
        self,
        event_name: str,
        event_data: Dict[str, Any],
        filter_data: Dict[str, Any] = None,
    ):
        """Emits an event calling all coroutines that have been registered."""
        for handler in self._handlers.get(event_name, []):
            args, kwargs = self._build_args_for_handler(handler, event_data)
            await handler(*args, **kwargs)

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

    def _build_args_for_handler(
        self, handler: Callable, event_data: Dict[str, Any]
    ) -> Tuple[List[Any], Dict[str, Any]]:
        positional = []
        args = []
        kwargs = {}

        num_positional = handler.__code__.co_posonlyargcount
        num_args = handler.__code__.co_argcount

        has_args = bool(handler.__code__.co_flags & 0x04)
        has_kwargs = bool(handler.__code__.co_flags & 0x08)

        names = (
            handler.__code__.co_varnames[: -(has_kwargs + has_args)]
            if has_kwargs or has_args
            else handler.__code__.co_varnames
        )

        if isinstance(handler, MethodType):  # Ignore self arg
            names = names[1:]
            num_positional -= 1

        for index, arg_name in enumerate(names):
            if arg_name.startswith("@"):  # Ignore PyTest
                continue

            if arg_name not in event_data:
                raise NameError(
                    f"No event value found to match the parameter '{arg_name}' defined on "
                    f"{handler.__name__} in {handler.__code__.co_filename} on line {handler.__code__.co_firstlineno}"
                )

            if index < num_positional:
                positional.append(event_data[arg_name])

            elif index < num_args + num_positional:
                args.append(event_data[arg_name])

            else:
                kwargs[arg_name] = event_data[arg_name]

        if has_kwargs:
            kwargs.update(
                {name: value for name, value in event_data.items() if name not in names}
            )

        return args, kwargs


class EventHandler:
    def __init__(self, event: str, callback: Callable[[], Coroutine]):
        self.event = event
        self.callback = callback

    def __get__(self, instance) -> Callable:
        return MethodType(self, instance)

    def __call__(self, *args, **kwargs) -> Coroutine:
        return self.callback(*args, **kwargs)


def event(event_name: str) -> Callable:
    def register(callback: Callable[[], Coroutine]) -> EventHandler:
        return EventHandler(event_name, callback)

    return register
