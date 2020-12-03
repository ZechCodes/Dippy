from collections import defaultdict
from dippy.labels.datastore import Datastore, Labels, NoLabelsProvided
from typing import Set, Sequence, Any


class MemoryStore(Datastore):
    """Simple datastore that keeps all labels in memory for the duration of the application's runtime."""

    def __init__(self):
        self.store = defaultdict(dict)

    @property
    def supported_object_types(self) -> Set[str]:
        """All object types that the memory store supports."""
        return {"server", "channel", "channel", "message", "user", "role"}

    def clear_label(self, label_name: str, **labels):
        """Clears a named label from all objects that match the provided labels. Providing no labels will raise an
        NoLabelsProvided exception."""
        if not labels:
            raise NoLabelsProvided()

        for object_labels in self._get_object_labels():
            if label_name in object_labels and self._labels_match(
                object_labels, labels
            ):
                del self.store[
                    object_labels["object_type"], object_labels["object_id"]
                ][label_name]

    def clear_labels(self, object_type: str, object_id: int):
        """Clears all labels from an object."""
        del self.store[object_type, object_id]

    def get_labels(self, **labels) -> Sequence[Labels]:
        """Gets all objects that match the given labels. This should respect the object_type and object_id labels. If
        no objects match the labels this will return an empty sequence."""
        return tuple(
            item
            for item in self._get_object_labels()
            if self._labels_match(item, labels)
        )

    def get_object_labels(self, object_type: str, object_id: int) -> Labels:
        """Gets the labels for a given object. If the object does not exist this should return a mapping containing
        only the object_type and object_id keys and their provided values."""
        return self._get_labels_for_object(object_type, object_id)

    def set_label(
        self, object_type: str, object_id: int, label_name: str, label_value: Any
    ):
        """Sets the named label for the requested object."""
        self.store[object_type, object_id][label_name] = label_value

    def update_label(self, label_name: str, label_value: Any, **labels):
        """Updates the named label for all objects that match the given labels. If an object matches but doesn't
        already have the named label, the label should be created."""
        for item in self._get_object_labels():
            if self._labels_match(item, labels):
                self.set_label(
                    item["object_type"], item["object_id"], label_name, label_value
                )

    def _get_labels_for_object(self, object_type: str, object_id: int) -> Labels:
        object_labels = self.store.get((object_type, object_id), {}).copy()
        object_labels["object_type"] = object_type
        object_labels["object_id"] = object_id
        return object_labels

    def _get_object_labels(self) -> Sequence[Labels]:
        for object_identifier in self.store:
            yield self._get_labels_for_object(*object_identifier)

    def _labels_match(self, object_labels: Labels, labels: Labels) -> bool:
        for key, value in labels.items():
            if key not in object_labels or object_labels[key] != value:
                return False

        return True
