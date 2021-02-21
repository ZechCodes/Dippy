from typing import Any

from dippy.labels.storage import StorageInterface
from collections import defaultdict


class MemoryStorage(StorageInterface):
    def __init__(self):
        self._storage = defaultdict(lambda: defaultdict(dict))

    def delete(self, object_type: str, object_id: int, key: str):
        if self.has(object_type, object_id, key):
            del self._storage[object_type][object_id][key]

    def get(
        self, object_type: str, object_id: int, key: str, default: Any = None
    ) -> Any:
        if not self.has(object_type, object_id, key):
            return default

        return self._storage[object_type][object_id][key]

    def has(self, object_type: str, object_id: int, key: str) -> bool:
        if object_type not in self._storage:
            return False

        if object_id not in self._storage[object_type]:
            return False

        if key not in self._storage[object_type][object_id]:
            return False

        return True

    def set(self, object_type: str, object_id: int, key: str, value: Any):
        self._storage[object_type][object_id][key] = value

    def setup(self):
        return
