import discord


class EventClient(discord.Client):
    def dispatch(self, event, *args, **kwargs):
        print(event, args, kwargs)
        return super().dispatch(event, *args, **kwargs)
