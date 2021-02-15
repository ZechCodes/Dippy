from dippy.events import EventHub
import asyncio


def test_event():
    result = False

    def callback(message):
        nonlocal result
        result = message.args[0]

    async def test(loop):
        hub = EventHub(loop=loop)
        watcher = hub.on("test_event", callback)
        await asyncio.sleep(0.1)
        hub.emit("test_event", "foobar")
        await asyncio.sleep(0.1)
        watcher.off()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(test(loop))
    assert result == "foobar"
