import asyncio
import dippy
import discord
import pytest


class MockClient(discord.Client):
    async def start(self, *args, **kwargs):
        """ Start the client on the event loop but don't connect to discord. """
        return


@pytest.fixture()
def message():
    m = discord.Message(
        state="TESTING",
        channel=None,
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


def test_bot_on_message(message):
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
