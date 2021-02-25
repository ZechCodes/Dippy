import asyncio

from dippy.labels import Labels
from dippy.labels.memory_storage import MemoryStorage
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
