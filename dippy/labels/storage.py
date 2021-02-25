from abc import abstractmethod
from bevy import Injectable
from typing import Any, Awaitable


class StorageInterface(Injectable):
    @abstractmethod
    async def delete(self, object_type: str, object_id: int, key: str):
        pass

    @abstractmethod
    async def get(
        self, object_type: str, object_id: int, key: str, default: Any = None
    ) -> Any:
        pass

    @abstractmethod
    async def has(self, object_type: str, object_id: int, key: str) -> bool:
        pass

    @abstractmethod
    async def set(self, object_type: str, object_id: int, key: str, value: Any):
        pass

    @abstractmethod
    async def setup(self):
        pass


class Labels(Injectable):
    storage: StorageInterface

    def __init__(self, object_type: str, object_id: int):
        self._object_id = object_id
        self._object_type = object_type

    def delete(self, key: str) -> Awaitable[None]:
        return self.storage.delete(self._object_type, self._object_id, key)

    def has(self, key: str) -> Awaitable[bool]:
        return self.storage.has(self._object_type, self._object_id, key)

    def get(self, key: str, default: Any = None) -> Any:
        return self.storage.get(self._object_type, self._object_id, key, default)

    def set(self, key: str, value: Any) -> Awaitable[None]:
        return self.storage.set(self._object_type, self._object_id, key, value)
