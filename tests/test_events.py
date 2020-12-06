from dippy.events import EventHub


def test_event_emit():
    data = "foobar"
    event_data = None

    def listener(event):
        nonlocal event_data
        event_data = event

    hub = EventHub()
    hub.on("testing", listener)
    hub.emit("testing", data)

    assert data == event_data


def test_event_emit_multiple_handlers():
    data = "foobar"
    event_data = []

    def listener_a(event):
        event_data.append("a")

    def listener_b(event):
        event_data.append("b")

    hub = EventHub()
    hub.on("testing", listener_a)
    hub.on("testing", listener_b)
    hub.emit("testing", data)

    assert sorted(event_data) == ["a", "b"]


def test_event_stop():
    data = "foobar"
    event_data = []

    def listener_a(event):
        event_data.append("a")

    def listener_b(event):
        event_data.append("b")

    hub = EventHub()
    hub.on("testing", listener_a)
    hub.on("testing", listener_b)
    hub.stop("testing", listener_a)
    hub.emit("testing", data)

    assert sorted(event_data) == ["b"]
