from dippy import Extension
from pytest import fixture
from .stub_client import StubClient
from .stub_extension_manager import StubExtensionManager
import asyncio
import bevy


@fixture
def loop():
    return asyncio.new_event_loop()


def create_client(loop):
    context = bevy.Context()
    context.add(context.create(StubExtensionManager))
    return context.create(StubClient, loop=loop, command_prefix="!")


def test_extension(loop):
    ran = False

    class TestExtension(Extension):
        def __init__(self):
            nonlocal ran
            ran = True

    client = create_client(loop)
    client.run("testing", kill_after=0.01)
    assert ran
