from __future__ import annotations
from typing import Any, Optional
from dippy.labels.storage import StorageInterface, NOT_SET, Label
from collections import defaultdict


class MemoryStorage(StorageInterface):
    def __init__(self):
        self._index: dict[str, dict[int, dict[str, Label]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        self._labels: list[Label] = []

    async def delete(self, object_type: str, object_id: int, key: str):
        if await self.has(object_type, object_id, key):
            self._labels.remove(self._index[object_type][object_id][key])
            del self._index[object_type][object_id][key]

    async def find(
        self,
        object_type: Optional[str] = None,
        object_id: Optional[int] = None,
        *,
        key: Optional[str] = None,
        value: Any = NOT_SET,
    ) -> list[Label]:
        result = []
        for label in self._labels:
            if object_type and object_type != label.type:
                continue

            if object_id and object_id != label.id:
                continue

            if key and key != label.key:
                continue

            if value is not NOT_SET and value != label.value:
                continue

            result.append(label)

        return result

    async def get(
        self, object_type: str, object_id: int, key: str, default: Any = None
    ) -> Any:
        if not await self.has(object_type, object_id, key):
            return default

        return self._index[object_type][object_id][key].value

    async def has(self, object_type: str, object_id: int, key: str) -> bool:
        return self._has(object_type, object_id, key)

    async def set(self, object_type: str, object_id: int, key: str, value: Any):
        if self._has(object_type, object_id, key):
            self._labels.remove(self._index[object_type][object_id][key])

        value_object = Label(object_type, object_id, key, value)
        self._labels.append(value_object)
        self._index[object_type][object_id][key] = value_object

    async def setup(self):
        return

    def _has(self, object_type: str, object_id: int, key: str) -> bool:
        if object_type not in self._index:
            return False

        if object_id not in self._index[object_type]:
            return False

        if key not in self._index[object_type][object_id]:
            return False

        return True
