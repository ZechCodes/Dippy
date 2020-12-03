from pytest import fixture
from dippy.labels.memory_store import MemoryStore
from dippy.labels.datastore import NoLabelsProvided


class TestMemoryStore:
    @fixture
    def datastore(self):
        return MemoryStore()

    @fixture
    def populated_store(self, datastore):
        datastore.set_label("message", 0, "foo", "bar")
        datastore.set_label("message", 0, "bar", "foo")
        datastore.set_label("server", 0, "name", "John")
        return datastore

    def test_supported_object_types(self, datastore):
        assert len(datastore.supported_object_types) > 0

    def test_set_get_label(self, datastore):
        datastore.set_label("message", 0, "foo", "bar")
        assert datastore.get_object_labels("message", 0)["foo"] == "bar"

    def test_clear_label(self, populated_store):
        populated_store.clear_label("foo", foo="bar")
        assert "foo" not in populated_store.get_object_labels("message", 0)

    def test_clear_labels(self, populated_store):
        populated_store.clear_labels("message", 0)
        assert populated_store.get_object_labels("message", 0) == {
            "object_type": "message",
            "object_id": 0,
        }

    def test_get_labels(self, populated_store):
        labels = populated_store.get_labels(name="John")
        assert labels
        assert labels[0]["object_id"] == 0 and labels[0]["object_type"] == "server"

    def test_get_labels_multiple_matches(self, populated_store):
        labels = populated_store.get_labels(object_id=0)
        assert len(labels) == 2

    def test_update_label(self, populated_store):
        populated_store.update_label("bar", "foooo", foo="bar")
        assert populated_store.get_object_labels("message", 0)["bar"] == "foooo"

    def test_update_label_create(self, populated_store):
        populated_store.update_label("new", "value", foo="bar")
        labels = populated_store.get_object_labels("message", 0)
        assert "new" in labels
        assert labels["new"] == "value"

    def test_update_multiple_objects(self, populated_store):
        populated_store.update_label("new", "value", object_id=0)
        assert populated_store.get_object_labels("message", 0)["new"] == "value"
        assert populated_store.get_object_labels("server", 0)["new"] == "value"
