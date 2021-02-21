from dippy.labels import Labels
from dippy.labels.memory_storage import MemoryStorage
import bevy


def test_memory_storage():
    context = bevy.Context()
    context.add(MemoryStorage())
    labels = context.create(Labels, "testing", 0)

    labels["test"] = "foobar"
    assert labels["test"] == "foobar"
    assert "test" in labels
    assert labels.get("test", "barfoo") == "foobar"

    del labels["test"]

    assert "test" not in labels
    assert labels.get("test", "barfoo") == "barfoo"
