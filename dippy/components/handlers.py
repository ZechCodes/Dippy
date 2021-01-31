from __future__ import annotations
from dippy.filters.filters import BaseFilter, GlobalFilter
from types import MethodType
from typing import Any, Callable, Coroutine, Dict, List, Tuple


class EventHandler:
    def __init__(
        self,
        event_name: str,
        callback: Callable[[], Coroutine],
        filters: BaseFilter,
        smart_args: bool = True,
    ):
        self._callback = callback
        self._event = event_name
        self._filters = filters
        self._smart_args = smart_args

    @property
    def event(self) -> str:
        return self._event

    @property
    def filters(self) -> BaseFilter:
        return self._filters

    def bind(self, instance) -> EventHandler:
        return EventHandler(
            self.event,
            MethodType(self._callback, instance),
            self.filters,
            self._smart_args,
        )

    def callback(self, **event_data) -> Any:
        args, kwargs = [], event_data
        if self._smart_args:
            args, kwargs = self._build_args_for_handler(self._callback, event_data)

        return self._callback(*args, **kwargs)

    def _build_args_for_handler(
        self, callback: Callable, event_data: Dict[str, Any]
    ) -> Tuple[List[Any], Dict[str, Any]]:
        positional = []
        args = []
        kwargs = {}

        num_positional = callback.__code__.co_posonlyargcount
        num_args = callback.__code__.co_argcount

        has_args = bool(callback.__code__.co_flags & 0x04)
        has_kwargs = bool(callback.__code__.co_flags & 0x08)

        names = (
            callback.__code__.co_varnames[: -(has_kwargs + has_args)]
            if has_kwargs or has_args
            else callback.__code__.co_varnames
        )[1:]
        num_positional -= 1

        for index, arg_name in enumerate(names):
            if arg_name.startswith("@"):  # Ignore PyTest
                continue

            if arg_name not in event_data:
                raise NameError(
                    f"No event value found to match the parameter '{arg_name}' defined on "
                    f"{callback.__name__} in {callback.__code__.co_filename} on line {callback.__code__.co_firstlineno}"
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


def event(event_name: str, filters: BaseFilter = GlobalFilter()) -> Callable:
    def register(callback: Callable[[], Coroutine]) -> EventHandler:
        return EventHandler(event_name, callback, filters)

    return register
