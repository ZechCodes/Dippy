import asyncio
import bevy
from .stub_client import StubClient
from .stub_extension_manager import StubExtensionManager


def test_client_create():
    loop = asyncio.new_event_loop()
    context = bevy.Context()
    context.add(context.create(StubExtensionManager))
    client = context.create(StubClient, loop=loop, command_prefix="!")
    client.run("testing", kill_after=0.01)
