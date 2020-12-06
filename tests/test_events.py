from pytest import raises
from dippy.events import EventHub
import asyncio


def test_event_emit():
    data = "foobar"
    event_data = None

    async def listener(event):
        nonlocal event_data
        event_data = event

    hub = EventHub()
    hub.on("testing", listener)
    asyncio.get_event_loop().run_until_complete(hub.emit("testing", data))

    assert data == event_data


def test_event_emit_multiple_handlers():
    data = "foobar"
    event_data = []

    async def listener_a(event):
        event_data.append("a")

    async def listener_b(event):
        event_data.append("b")

    hub = EventHub()
    hub.on("testing", listener_a)
    hub.on("testing", listener_b)
    asyncio.get_event_loop().run_until_complete(hub.emit("testing", data))

    assert sorted(event_data) == ["a", "b"]


def test_event_stop():
    data = "foobar"
    event_data = []

    async def listener_a(event):
        event_data.append("a")

    async def listener_b(event):
        event_data.append("b")

    hub = EventHub()
    hub.on("testing", listener_a)
    hub.on("testing", listener_b)
    hub.stop("testing", listener_a)
    asyncio.get_event_loop().run_until_complete(hub.emit("testing", data))

    assert sorted(event_data) == ["b"]


def test_event_stop():
    data = "foobar"
    event_data = []

    async def listener_a(event):
        event_data.append("a")

    async def listener_b(event):
        event_data.append("b")

    hub = EventHub()
    hub.on("testing", listener_a)
    hub.on("testing", listener_b)
    hub.stop("testing", listener_a)
    asyncio.get_event_loop().run_until_complete(hub.emit("testing", data))

    assert sorted(event_data) == ["b"]


def test_event_register_function():
    def listener(event):
        return

    hub = EventHub()
    with raises(ValueError):
        hub.on("testing", listener)
