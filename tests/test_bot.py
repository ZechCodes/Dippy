import asyncio
import dippy
import discord
import pytest


class MockClient(discord.Client):
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
def message(text_channel):
    return discord.Message(
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
        },
    )


def test_bot_start_up():
    bot = dippy.Bot.create("Test Bot", __file__)

    with pytest.raises(discord.errors.LoginFailure):
        bot.run("NOT A TOKEN")


def test_bot_on_message(message, text_channel, guild):
    ran = False

    loop = asyncio.new_event_loop()
    bot = dippy.Bot.create("Test Bot", __file__, client=MockClient, loop=loop)

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
