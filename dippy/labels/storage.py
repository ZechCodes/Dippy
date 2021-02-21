from abc import abstractmethod
from bevy import Injectable
from typing import Any


class StorageInterface(Injectable):
    @abstractmethod
    def delete(self, object_type: str, object_id: int, key: str):
        pass

    @abstractmethod
    def get(
        self, object_type: str, object_id: int, key: str, default: Any = None
    ) -> Any:
        pass

    @abstractmethod
    def has(self, object_type: str, object_id: int, key: str) -> bool:
        pass

    @abstractmethod
    def set(self, object_type: str, object_id: int, key: str, value: Any):
        pass

    @abstractmethod
    def setup(self):
        pass


class Labels(Injectable):
    storage: StorageInterface

    def __init__(self, object_type: str, object_id: int):
        self._object_id = object_id
        self._object_type = object_type

    def __contains__(self, key: str) -> bool:
        return self.storage.has(self._object_type, self._object_id, key)

    def __delitem__(self, key: str):
        self.storage.delete(self._object_type, self._object_id, key)

    def __getitem__(self, key: str) -> Any:
        if key not in self:
            raise KeyError(key)
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.storage.set(self._object_type, self._object_id, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return self.storage.get(self._object_type, self._object_id, key, default)
