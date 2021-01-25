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
def component_base():
    dippy.Component.__components__ = []
    return dippy.Component


@pytest.fixture()
def guild_fixture():
    class CustomGuild(discord.Guild):
        def __repr__(self):
            attrs = ("id", "name", "chunked")
            resolved = ["%s=%r" % (attr, getattr(self, attr)) for attr in attrs]
            resolved.append("member_count=%r" % getattr(self, "_member_count", None))
            return "<Guild %s>" % " ".join(resolved)

    return CustomGuild(
        state="TESTING",
        data={
            "name": "Test Guild",
            "id": 0,
        },
    )


@pytest.fixture()
def user_fixture():
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
def text_channel(guild_fixture):
    return discord.TextChannel(
        state="TESTING",
        guild=guild_fixture,
        data={
            "name": "Test Text Channel",
            "id": 0,
            "type": "TEXT",
            "position": 0,
        },
    )


@pytest.fixture()
def dm_channel(guild_fixture, user_fixture):
    class CustomDMChannel(discord.DMChannel):
        def __init__(self, *, me, state, data):
            self._state = state
            self.recipient = user_fixture
            self.me = me
            self.id = int(data["id"])

    return CustomDMChannel(
        state="TESTING",
        me=user_fixture,
        data={
            "id": 0,
        },
    )


@pytest.fixture()
def message_fixture(text_channel, user_fixture):
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
            "author": user_fixture,
            "member": user_fixture,
            "mentions": [],
            "mention_roles": [],
            "call": None,
            "flags": [],
        },
    )


@pytest.fixture()
def direct_message(dm_channel, user_fixture):
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
            "author": user_fixture,
            "member": user_fixture,
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


def test_bot_on_message(message_fixture, text_channel, guild_fixture):
    ran = False

    loop = asyncio.new_event_loop()
    bot = dippy.create("Test Bot", __file__, client=MockClient, loop=loop)

    async def on_message(message, channel, guild):
        nonlocal ran
        assert channel is text_channel
        assert guild is guild
        assert message is message_fixture
        ran = True
        await bot.client.close()

    async def runner():
        bot.client.dispatch("message", message_fixture)

    bot.events.on("message", on_message)
    loop.create_task(runner())
    bot.run("NOT A TOKEN")

    assert ran


def test_bot_on_message_using_bot(message_fixture, text_channel, guild_fixture):
    ran = 0

    loop = asyncio.new_event_loop()
    bot = dippy.create(
        "Test Bot", __file__, client=MockBot, loop=loop, command_prefix="!"
    )

    async def watch_for_message(channel, guild, message):
        nonlocal ran
        assert channel is text_channel
        assert guild is guild_fixture
        assert message is message_fixture
        ran += 2
        await bot.client.close()

    async def on_message(m):
        nonlocal ran
        ran += 1

    async def runner():
        bot.client.dispatch("message", message_fixture)

    bot.client.event(on_message)
    bot.events.on("message", watch_for_message)
    loop.create_task(runner())
    bot.run("NOT A TOKEN")

    assert ran == 3


def test_bot_on_direct_message(direct_message, dm_channel, user_fixture):
    ran = False

    loop = asyncio.new_event_loop()
    bot = dippy.create("Test Bot", __file__, client=MockClient, loop=loop)

    async def on_message(channel, recipient, message):
        nonlocal ran
        assert channel is dm_channel
        assert recipient is user_fixture
        assert message is direct_message
        ran = True
        await bot.client.close()

    async def runner():
        bot.client.dispatch("message", direct_message)

    bot.events.on("direct_message", on_message)
    loop.create_task(runner())
    bot.run("NOT A TOKEN")

    assert ran


def test_component_on_message(
    message_fixture, text_channel, guild_fixture, component_base
):
    ran = False

    class TestComponent(component_base):
        @dippy.event("message")
        async def watch_for_messages(self, channel, guild, message):
            nonlocal ran
            assert channel is text_channel
            assert guild is guild_fixture
            assert message is message_fixture
            ran = True

    loop = asyncio.new_event_loop()
    bot = dippy.create("Test Bot", __file__, client=MockClient, loop=loop)

    async def runner():
        bot.client.dispatch("message", message_fixture)

    loop.create_task(runner())
    bot.run("NOT A TOKEN")

    assert ran
