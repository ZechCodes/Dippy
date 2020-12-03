from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Mapping, Sequence, Set


Labels = Mapping[str, Any]


class NoLabelsProvided(Exception):
    ...


class Datastore(ABC):
    """Abstract base class for datastore providers.

    All datastore providers should implement this interface so that Bevy can locate the
    the appropriate instance."""

    @property
    @abstractmethod
    def supported_object_types(self) -> Set[str]:
        """All object types that the datastore supports. These should all be in casefold form."""
        ...

    @abstractmethod
    def clear_label(self, label_name: str, **labels):
        """Clears a named label from all objects that match the provided labels. Providing no labels will raise an
        NoLabelsProvided exception."""
        ...

    @abstractmethod
    def clear_labels(self, object_type: str, object_id: int):
        """Clears all labels from an object."""
        ...

    @abstractmethod
    def get_labels(self, **labels) -> Sequence[Labels]:
        """Gets all objects that match the given labels. This should respect the object_type and object_id labels. If
        no objects match the labels this will return an empty sequence."""
        ...

    @abstractmethod
    def get_object_labels(self, object_type: str, object_id: int) -> Labels:
        """Gets the labels for a given object. If the object does not exist this should return a mapping containing
        only the object_type and object_id keys and their provided values."""
        ...

    @abstractmethod
    def set_label(
        self, object_type: str, object_id: int, label_name: str, label_value: Any
    ):
        """Sets the named label for the requested object."""
        ...

    @abstractmethod
    def update_label(self, label_name: str, label_value: Any, **labels):
        """Updates the named label for all objects that match the given labels. If an object matches but doesn't
        already have the named label, the label should be created."""
        ...
