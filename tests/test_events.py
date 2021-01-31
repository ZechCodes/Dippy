from pytest import raises
from dippy.events import EventHub
import asyncio


def test_event_emit():
    data = {"arg": "foobar"}
    event_data = None

    async def listener(arg):
        nonlocal event_data
        event_data = arg

    hub = EventHub()
    hub.on("testing", listener)
    asyncio.new_event_loop().run_until_complete(hub.emit("testing", data))

    assert data["arg"] == event_data


def test_event_emit_multiple_handlers():
    data = {"arg": "foobar"}
    event_data = []

    async def listener_a(arg):
        event_data.append("a")

    async def listener_b(arg):
        event_data.append("b")

    hub = EventHub()
    hub.on("testing", listener_a)
    hub.on("testing", listener_b)
    asyncio.new_event_loop().run_until_complete(hub.emit("testing", data))

    assert sorted(event_data) == ["a", "b"]


def test_event_stop():
    data = {"arg": "foobar"}
    event_data = []

    async def listener_a(arg):
        event_data.append("a")

    async def listener_b(arg):
        event_data.append("b")

    hub = EventHub()
    hub.on("testing", listener_a)
    hub.on("testing", listener_b)
    hub.off("testing", listener_a)
    asyncio.new_event_loop().run_until_complete(hub.emit("testing", data))

    assert sorted(event_data) == ["b"]


def test_keyward_args():
    data = {"arg": "foo", "arg2": "bar"}
    event_data = []

    async def listener(arg, *, arg2):
        event_data.append(f"{arg}{arg2}")

    hub = EventHub()
    hub.on("testing", listener)

    asyncio.new_event_loop().run_until_complete(hub.emit("testing", data))

    assert event_data == ["foobar"]


def test_event_register_function():
    def listener(event):
        return

    hub = EventHub()
    with raises(ValueError):
        hub.on("testing", listener)
