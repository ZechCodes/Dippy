import dippy
import asyncio


class StubClient(dippy.Client):
    async def start(self, *args, **kwargs):
        """Allow the bot to begin without a valid token.

        It will not be authenticated so will not connect to the API."""

        async def noop():
            await asyncio.sleep(0.001)

        while not self.is_closed():
            await noop()

    def run(self, *args, kill_after: float = -1, **kwargs):
        if kill_after > 0:

            async def kill(bot: dippy.Client):
                await asyncio.sleep(kill_after)
                await bot.close()

            self.loop.create_task(kill(self))

        super().run(*args, **kwargs)
