import dippy
import discord
import pytest


def test_bot_start_up():
    bot = dippy.Bot.create("Test Bot", __file__)

    with pytest.raises(discord.errors.LoginFailure):
        bot.run("NOT A TOKEN")
