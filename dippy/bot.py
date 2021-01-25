from dippy.components import ComponentManager
from dippy.config import ConfigManager
from dippy.config.loaders import yaml_loader
from dippy.config.manager import ConfigLoader
from dippy.events import EventHub
from dippy.logging import Logging
from typing import Any, Callable, Dict, Optional, Sequence, Type, Union
import bevy
import datetime
import discord
import pathlib


class Bot(bevy.Injectable):
    component_manager: ComponentManager
    config_manager: ConfigManager
    logger_factory: bevy.Factory[Logging]
    events: EventHub
    client: discord.Client

    def __init__(self, bot_name: str, application_path: Union[pathlib.Path, str], /):
        self.bot_name = bot_name
        self.path = self._tidy_app_path(application_path)

        self.logger: Logging = self.logger_factory(self.bot_name)
        self.logger.setup_logger()

        self.logger.info(
            f"Starting bot\n"
            f"  Name: {self.bot_name!r}\n"
            f"  Path: {self.path.resolve()} ({'EXISTS' if self.path.exists() else 'DOES NOT EXIST'})\n"
        )

        self.component_manager.load_components(pathlib.Path(application_path))
        self.component_manager.create_components()

        self._setup_event_dispatch()

    def run(self, token: str):
        self.client.run(token)

    async def on_message(self, message: discord.Message):
        filter_data = self._get_user_event_data(message.author)
        filter_data.update(self._get_message_event_data(message))
        if isinstance(message.channel, discord.DMChannel):
            await self.events.emit(
                "direct_message",
                {
                    "message": message,
                    "channel": message.channel,
                    "recipient": message.channel.recipient,
                },
                filter_data,
            )
        elif isinstance(message.channel, discord.GroupChannel):
            await self.events.emit(
                "group_message",
                {
                    "message": message,
                    "channel": message.channel,
                },
                filter_data,
            )
        else:
            await self.events.emit(
                "message",
                {
                    "message": message,
                    "channel": message.channel,
                    "guild": message.guild,
                },
                filter_data,
            )

    async def on_ready(self):
        await self.events.emit("ready")

    async def on_error(self, event, *args, **kwargs):
        await self.events.emit(
            "error", {"event": event, "arguments": args, "keyword_arguments": kwargs}
        )

    async def on_typing(
        self,
        channel: Union[discord.DMChannel, discord.GroupChannel, discord.TextChannel],
        user: Union[discord.User, discord.Member],
        when: datetime.datetime,
    ):
        data = {"channel": channel, "started": when}
        event = "member_typing"
        filter_data = {"channel_id": channel.id}
        filter_data.update(self._get_user_event_data(user))
        if isinstance(channel, (discord.GroupChannel, discord.DMChannel)):
            event = (
                "group_typing"
                if isinstance(channel, discord.GroupChannel)
                else "dm_typing"
            )
            data["user"] = user
        else:
            data["member"] = user

        await self.events.emit(event, data, filter_data)

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        data = {
            "channel_id": payload.channel_id,
            "message_id": payload.message_id,
            "message": payload.cached_message,
        }
        event = "chat_message_deleted"
        if payload.guild_id:
            event = "message_deleted"
            data["guild_id"] = payload.guild_id

        filter_data = data.copy()
        filter_data.pop("message")

        await self.events.emit(event, data, filter_data)

    async def on_raw_bulk_message_delete(
        self, payload: discord.RawBulkMessageDeleteEvent
    ):
        data = {
            "channel_id": payload.channel_id,
            "message_ids": payload.message_ids,
            "messages": payload.cached_messages,
        }
        filter_data = {"channel_id": payload.channel_id}
        event = "chat_messages_bulk_deleted"
        if payload.guild_id:
            event = "messages_bulk_deleted"
            data["guild_id"] = payload.guild_id
            filter_data["guild_id"] = payload.guild_id

        await self.events.emit(event, data, filter_data)

    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        channel = self.client.get_channel(payload.channel_id)
        data = {
            "channel": channel,
            "message_id": payload.message_id,
            "message": payload.cached_message,
            "data": payload.data,
        }
        filter_data = {
            "channel_id": payload.channel_id,
            "message_id": payload.message_id,
        }
        event = "chat_message_edited"
        if isinstance(channel, discord.TextChannel):
            event = "message_edited"
            data["guild"] = channel.guild
            filter_data["guild_id"] = channel.guild.id

        await self.events.emit(event, data, filter_data)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        channel = self.client.get_channel(payload.channel_id)
        data = {
            "channel": channel,
            "message_id": payload.message_id,
            "emoji": payload.emoji,
        }
        filter_data = {
            "channel_id": channel.id,
            "message_id": payload.message_id,
            "emoji_ids": {
                payload.emoji.id,
            },
        }
        event = "chat_reaction_added"
        if payload.guild_id:
            event = "reaction_added"
            data["guild"] = self.client.get_guild(payload.guild_id)
            data["member"] = payload.member
            filter_data["guild_id"] = payload.guild_id
            filter_data.update(
                self._get_user_event_data(data["guild"].get_member(payload.user_id))
            )
        else:
            data["user"] = self.client.get_user(payload.user_id)
            filter_data.update(
                self._get_user_event_data(self.client.get_user(payload.user_id))
            )

        await self.events.emit(event, data, filter_data)

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        channel = self.client.get_channel(payload.channel_id)
        data = {
            "channel": channel,
            "message_id": payload.message_id,
            "emoji": payload.emoji,
        }
        filter_data = {
            "channel_id": channel.id,
            "message_id": payload.message_id,
            "emoji_ids": {
                payload.emoji.id,
            },
        }
        event = "chat_reaction_added"
        if payload.guild_id:
            event = "reaction_added"
            data["guild"] = self.client.get_guild(payload.guild_id)
            data["member"] = payload.member
            filter_data.update(
                self._get_user_event_data(data["guild"].get_member(payload.user_id))
            )
        else:
            data["user"] = self.client.get_user(payload.user_id)
            filter_data.update(
                self._get_user_event_data(self.client.get_user(payload.user_id))
            )

        await self.events.emit(event, data, filter_data)

    async def on_raw_reaction_clear_emoji(
        self, payload: discord.RawReactionClearEmojiEvent
    ):
        channel = self.client.get_channel(payload.channel_id)
        data = {
            "channel": channel,
            "message_id": payload.message_id,
            "emoji": payload.emoji,
        }
        filter_data = {
            "channel_id": channel.id,
            "message_id": payload.message_id,
            "emoji_ids": {
                payload.emoji.id,
            },
        }
        event = "chat_reactions_emoji_cleared"
        if payload.guild_id:
            event = "reactions_emoji_cleared"
            data["guild"] = self.client.get_guild(payload.guild_id)
            filter_data["guild_id"] = payload.guild_id

        await self.events.emit(event, data, filter_data)

    async def on_raw_reaction_clear(self, payload: discord.RawReactionClearEvent):
        channel = self.client.get_channel(payload.channel_id)
        data = {
            "channel": channel,
            "message_id": payload.message_id,
        }
        filter_data = {"channel_id": channel.id, "message_id": payload.message_id}
        event = "chat_reactions_cleared"
        if payload.guild_id:
            event = "reactions_cleared"
            data["guild"] = self.client.get_guild(payload.guild_id)
            filter_data["guild_id"] = payload.guild_id

        await self.events.emit(event, data, filter_data)

    async def on_member_join(self, member: discord.Member):
        await self.events.emit(
            "member_joined",
            {"member": member, "guild": member.guild},
            self._get_user_event_data(member),
        )

    async def on_member_remove(self, member: discord.Member):
        await self.events.emit(
            "member_left",
            {"member": member, "guild": member.guild},
            self._get_user_event_data(member),
        )

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        data = {
            "guild": after.guild,
            "member": after,
        }
        filter_data = self._get_user_event_data(after)

        if before.status != after.status:
            _data = data.copy()
            _data["status"] = after.status
            _data["previous"] = before.status
            await self.events.emit("member_status_changed", _data, filter_data)

        if before.activity != after.activity:
            _data = data.copy()
            _data["activity"] = after.activity
            _data["previous"] = before.activity
            await self.events.emit("member_activity_changed", _data, filter_data)

        if before.nick != after.nick:
            _data = data.copy()
            _data["nickname"] = after.nick
            _data["previous"] = before.nick
            await self.events.emit("member_nickname_changed", _data, filter_data)

        if before.roles != after.roles:
            _data = data.copy()
            _data["roles"] = after.roles
            _data["previous"] = before.roles
            await self.events.emit("member_roles_changed", _data, filter_data)

        if before.pending != after.pending:
            _data = data.copy()
            _data["pending"] = after.pending
            _data["previous"] = before.pending
            await self.events.emit("member_roles_changed", _data, filter_data)

    async def on_user_update(self, before: discord.User, after: discord.User):
        data = {
            "user": after,
        }
        filter_data = self._get_user_event_data(after)

        if before.avatar != after.avatar:
            _data = data.copy()
            _data["avatar"] = after.avatar
            _data["previous"] = before.avatar
            await self.events.emit("user_avatar_changed", _data, filter_data)

        if before.name != after.name:
            _data = data.copy()
            _data["name"] = after.name
            _data["previous"] = before.name
            await self.events.emit("user_name_changed", _data, filter_data)

        if before.discriminator != after.discriminator:
            _data = data.copy()
            _data["discriminator"] = after.discriminator
            _data["previous"] = before.discriminator
            await self.events.emit("user_discriminator_changed", _data, filter_data)

    def _get_user_event_data(
        self, user: Union[discord.Member, discord.User]
    ) -> Dict[str, Any]:
        data = {"user_id": user.id}
        if isinstance(user, discord.Member):
            data["guild_id"] = user.guild.id
            data["role_ids"] = set(role.id for role in user.roles)

        return data

    def _get_message_event_data(
        self, message: discord.Message, *, ignore_reactions: bool = False
    ) -> Dict[str, Any]:
        data = {"message_id": message.id, "channel_id": message.channel.id}
        if message.guild:
            data["guild_id"] = message.guild.id

        if not ignore_reactions:
            data["emoji_ids"] = set(reaction.emoji.id for reaction in message.reactions)

        return data

    def _setup_event_dispatch(self):
        # Try to use the listen method if possible, otherwise fallback to using the event method
        # The listen method is preferred as it won't override any existing event handlers defined on the client
        register: Callable[[Callable], None] = (
            self.client.listen()
            if hasattr(self.client, "listen")
            else self.client.event
        )
        register(self.on_error)
        register(self.on_member_join)
        register(self.on_member_remove)
        register(self.on_member_update)
        register(self.on_message)
        register(self.on_raw_bulk_message_delete)
        register(self.on_raw_message_delete)
        register(self.on_raw_message_edit)
        register(self.on_raw_reaction_add)
        register(self.on_raw_reaction_clear)
        register(self.on_raw_reaction_clear_emoji)
        register(self.on_raw_reaction_remove)
        register(self.on_ready)
        register(self.on_typing)
        register(self.on_user_update)

    def _tidy_app_path(self, path: Union[pathlib.Path, str]) -> pathlib.Path:
        tidy_path = pathlib.Path(path)
        return tidy_path if tidy_path.is_dir() else tidy_path.parent

    @classmethod
    def create(
        cls,
        bot_name: str,
        application_path: Union[pathlib.Path, str],
        /,
        *,
        client: Optional[Type[discord.Client]] = None,
        config_dir: str = "config",
        config_files: Sequence[str] = ("development.yaml", "production.yaml"),
        loaders: Sequence[ConfigLoader] = (yaml_loader,),
        **client_options,
    ) -> "Bot":
        context = bevy.Context()
        context.add(
            ConfigManager(
                application_path,
                config_dir,
                config_files=config_files,
                config_loaders=loaders,
            )
        )
        context.add(context.create(ComponentManager, bot_name))

        context.add((client if client else discord.Client)(**client_options))

        bot = context.create(cls, bot_name, application_path)
        context.add(bot)

        return bot
