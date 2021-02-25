from typing import Any

from dippy.labels.storage import StorageInterface
from collections import defaultdict


class MemoryStorage(StorageInterface):
    def __init__(self):
        self._storage = defaultdict(lambda: defaultdict(dict))

    async def delete(self, object_type: str, object_id: int, key: str):
        if await self.has(object_type, object_id, key):
            del self._storage[object_type][object_id][key]

    async def get(
        self, object_type: str, object_id: int, key: str, default: Any = None
    ) -> Any:
        if not await self.has(object_type, object_id, key):
            return default

        return self._storage[object_type][object_id][key]

    async def has(self, object_type: str, object_id: int, key: str) -> bool:
        if object_type not in self._storage:
            return False

        if object_id not in self._storage[object_type]:
            return False

        if key not in self._storage[object_type][object_id]:
            return False

        return True

    async def set(self, object_type: str, object_id: int, key: str, value: Any):
        self._storage[object_type][object_id][key] = value

    async def setup(self):
        return
