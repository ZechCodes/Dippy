from dippy.labels import Labels
from dippy.labels.memory_storage import MemoryStorage
import asyncio
import bevy


def test_memory_storage():
    async def test():
        context = bevy.Context()
        context.add(MemoryStorage())
        labels = context.create(Labels, "testing", 0)

        await labels.set(
            "test",
            "foobar",
        )
        assert await labels.get("test") == "foobar"
        assert await labels.get("test", "barfoo") == "foobar"
        assert labels.has("test")

        await labels.delete("test")

        assert not await labels.has("test")
        assert await labels.get("test", "barfoo") == "barfoo"

    asyncio.new_event_loop().run_until_complete(test())


def test_memory_storage_find():
    async def test():
        context = bevy.Context()
        storage = MemoryStorage()
        context.add(storage)

        labels_a = context.create(Labels, "type_a", 0)
        await asyncio.gather(
            labels_a.set("key_a", "foobar"),
            labels_a.set("key_b", "barfoo"),
            labels_a.set("key_c", "hello_world"),
        )

        labels_b = context.create(Labels, "type_b", 324)
        await asyncio.gather(
            labels_b.set("key_a", "barfoo"),
            labels_b.set("key_d", "foobar"),
            labels_b.set("key_e", "hi planet"),
        )

        assert [label.value for label in await storage.find(key="key_a")] == [
            "foobar",
            "barfoo",
        ]

        assert [label.key for label in await storage.find(object_id=324)] == [
            "key_a",
            "key_d",
            "key_e",
        ]

        assert [label.key for label in await storage.find(value="barfoo")] == [
            "key_b",
            "key_a",
        ]

        assert [label.key for label in await storage.find(object_type="type_b")] == [
            "key_a",
            "key_d",
            "key_e",
        ]

        assert [
            label.key
            for label in await storage.find(
                object_type="type_b", object_id=324, key="key_e", value="hi planet"
            )
        ] == [
            "key_e",
        ]

        assert [
            label.key for label in await storage.find("type_a", value="hi planet")
        ] == []

    asyncio.new_event_loop().run_until_complete(test())
