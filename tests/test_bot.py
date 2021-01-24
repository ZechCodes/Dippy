import asyncio
import dippy
import discord
import discord.ext.commands
import pytest


class MockClient(discord.Client):
    async def start(self, *args, **kwargs):
        """ Start the client on the event loop but don't connect to discord. """
        return


class MockBot(discord.ext.commands.Bot):
    async def start(self, *args, **kwargs):
        """ Start the client on the event loop but don't connect to discord. """
        return


@pytest.fixture()
def guild():
    return discord.Guild(
        state="TESTING",
        data={
            "name": "Test Guild",
            "id": 0,
        },
    )


@pytest.fixture()
def user():
    return discord.User(
        state="TESTING",
        data={
            "username": "Test User",
            "id": 0,
            "discriminator": "0000",
            "avatar": "TEST AVATAR",
        },
    )


@pytest.fixture()
def text_channel(guild):
    return discord.TextChannel(
        state="TESTING",
        guild=guild,
        data={
            "name": "Test Text Channel",
            "id": 0,
            "type": "TEXT",
            "position": 0,
        },
    )


@pytest.fixture()
def dm_channel(guild, user):
    class CustomDMChannel(discord.DMChannel):
        def __init__(self, *, me, state, data):
            self._state = state
            self.recipient = user
            self.me = me
            self.id = int(data["id"])

    return CustomDMChannel(
        state="TESTING",
        me=user,
        data={
            "id": 0,
        },
    )


@pytest.fixture()
def message(text_channel, user):
    class CustomMessage(discord.Message):
        def _handle_member(self, member):
            self.member = member

        def _handle_author(self, author):
            self.author = author

    return CustomMessage(
        state="TESTING",
        channel=text_channel,
        data={
            "id": 0,
            "webhook_id": 0,
            "attachments": [],
            "embeds": [],
            "application": None,
            "activity": None,
            "edited_timestamp": None,
            "type": None,
            "pinned": False,
            "mention_everyone": False,
            "tts": False,
            "content": "This is content for a Test Message",
            "author": user,
            "member": user,
            "mentions": [],
            "mention_roles": [],
            "call": None,
            "flags": [],
        },
    )


@pytest.fixture()
def direct_message(dm_channel, user):
    class CustomMessage(discord.Message):
        def _handle_member(self, member):
            self.member = member

        def _handle_author(self, author):
            self.author = author

    return CustomMessage(
        state="TESTING",
        channel=dm_channel,
        data={
            "id": 0,
            "webhook_id": 0,
            "attachments": [],
            "embeds": [],
            "application": None,
            "activity": None,
            "edited_timestamp": None,
            "type": None,
            "pinned": False,
            "mention_everyone": False,
            "tts": False,
            "content": "This is content for a Test Message",
            "author": user,
            "member": user,
            "mentions": [],
            "mention_roles": [],
            "call": None,
            "flags": [],
        },
    )


def test_bot_start_up():
    bot = dippy.Bot.create("Test Bot", __file__)

    with pytest.raises(discord.errors.LoginFailure):
        bot.run("NOT A TOKEN")


def test_bot_on_message(message, text_channel, guild):
    ran = False

    loop = asyncio.new_event_loop()
    bot = dippy.create("Test Bot", __file__, client=MockClient, loop=loop)

    async def on_message(m: discord.Message, c: discord.TextChannel, g: discord.Guild):
        nonlocal ran
        assert c is text_channel
        assert g is guild
        assert m is message
        ran = True
        await bot.client.close()

    async def runner():
        bot.client.dispatch("message", message)

    bot.events.on("message", on_message)
    loop.create_task(runner())
    bot.run("NOT A TOKEN")

    assert ran


def test_bot_on_message_using_bot(message, text_channel, guild):
    ran = 0

    loop = asyncio.new_event_loop()
    bot = dippy.create(
        "Test Bot", __file__, client=MockBot, loop=loop, command_prefix="!"
    )

    async def watch_for_message(
        m: discord.Message, c: discord.TextChannel, g: discord.Guild
    ):
        nonlocal ran
        assert c is text_channel
        assert g is guild
        assert m is message
        ran += 2
        await bot.client.close()

    async def on_message(m):
        nonlocal ran
        ran += 1

    async def runner():
        bot.client.dispatch("message", message)

    bot.client.event(on_message)
    bot.events.on("message", watch_for_message)
    loop.create_task(runner())
    bot.run("NOT A TOKEN")

    assert ran == 3


def test_bot_on_direct_message(direct_message, dm_channel, user):
    ran = False

    loop = asyncio.new_event_loop()
    bot = dippy.create("Test Bot", __file__, client=MockClient, loop=loop)

    async def on_message(m: discord.Message, c: discord.DMChannel, r: discord.User):
        nonlocal ran
        assert c is dm_channel
        assert r is user
        assert m is direct_message
        ran = True
        await bot.client.close()

    async def runner():
        bot.client.dispatch("message", direct_message)

    bot.events.on("direct_message", on_message)
    loop.create_task(runner())
    bot.run("NOT A TOKEN")

    assert ran


def test_component_on_message(message, text_channel, guild):
    ran = False

    class TestComponent(dippy.Component):
        @dippy.event("message")
        async def watch_for_messages(self, m, c, g):
            nonlocal ran
            assert c is text_channel
            assert g is guild
            assert m is message
            ran = True

    loop = asyncio.new_event_loop()
    bot = dippy.create("Test Bot", __file__, client=MockClient, loop=loop)

    async def runner():
        bot.client.dispatch("message", message)

    loop.create_task(runner())
    bot.run("NOT A TOKEN")

    assert ran
