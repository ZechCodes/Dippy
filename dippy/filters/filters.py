from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, Dict, Iterable


ChannelID = int
EventData = Dict[str, Any]
GuildID = int
Label = str
MessageID = int
ReactionID = int
RoleID = int
UserID = int


class AggregationType(Enum):
    AND = auto()
    OR = auto()
    NONE = auto()


class BaseFilter(ABC):
    @abstractmethod
    def matches(self, event: EventData) -> bool:
        """ Determines if the event matches the filter. """
        return False

    def __and__(self, filter_: BaseFilter) -> AggregateFilter:
        return AggregateFilter(
            self, filter_, method=all, aggregation_type=AggregationType.AND
        )

    def __or__(self, filter_: BaseFilter) -> AggregateFilter:
        return AggregateFilter(
            self, filter_, method=any, aggregation_type=AggregationType.OR
        )

    def __invert__(self) -> InverseFilter:
        return InverseFilter(self)

    def __call__(self, event: EventData) -> bool:
        return self.matches(event)


class InverseFilter(BaseFilter):
    """ This filter takes another filter and matches the inverse of that filter. """

    def __init__(self, filter_: BaseFilter):
        self.filter = filter_

    def matches(self, event: EventData) -> bool:
        """ Matches all events that do not match the underlying filter. """
        return not self.filter.matches(event)


class AggregateFilter(BaseFilter):
    """This filter aggregates the results of multiple filters using an aggregate method.

    This filter takes a series of filters, an aggregate method that must take an iterable of bools and returns a bool,
    and finally an aggregation type to allow the aggregate to capture other filters.
    """

    def __init__(
        self,
        *filters: BaseFilter,
        method: Callable[[Iterable[bool]], bool],
        aggregation_type: AggregationType = AggregationType.NONE,
    ):
        self.aggregation_type = aggregation_type
        self.filters = filters
        self.method = method

    def matches(self, event: EventData) -> bool:
        """ Passes the event to all filters and gives the aggregate iterable result to the aggregation method. """
        return self.method(filter_.matches(event) for filter_ in self.filters)

    def __and__(self, filter_: BaseFilter) -> BaseFilter:
        if self.aggregation_type == AggregationType.AND:
            self.filters = (*self.filters, filter_)
            return self
        return super().__and__(filter_)

    def __or__(self, filter_: BaseFilter) -> BaseFilter:
        if self.aggregation_type == AggregationType.OR:
            self.filters = (*self.filters, filter_)
            return self
        return super().__or__(filter_)


class GlobalFilter(BaseFilter):
    """ This filter will match any event. """

    def matches(self, _: EventData) -> bool:
        """ Matches all events. """
        return True


class LabelFilter(BaseFilter):
    """ This filter only matches events that have at least one matching label. """

    def __init__(self, *labels: Label):
        self.labels = set(labels)

    def matches(self, event: EventData) -> bool:
        """ Checks that an event has at least one label in common with the current filter. """
        return bool(self.labels & event.get("labels", set()))


class GuildFilter(BaseFilter):
    """ This filter only matches events that match one of the guilds. """

    def __init__(self, *guild_ids: GuildID):
        self.guild_ids = guild_ids

    def matches(self, event: EventData) -> bool:
        """ Checks that the event guild ID matches any of the guild IDs given to the filter. """
        return "guild_id" in event and event["guild_id"] in self.guild_ids


class ChannelFilter(BaseFilter):
    """ This filter only matches events that match one of the channels. """

    def __init__(self, *channel_ids: ChannelID):
        self.channel_ids = channel_ids

    def matches(self, event: EventData) -> bool:
        """ Checks that the event channel ID matches any of the channel IDs given to the filter. """
        return "channel_id" in event and event["channel_id"] in self.channel_ids


class UserFilter(BaseFilter):
    """ This filter only matches events that match one of the users. """

    def __init__(self, *user_ids: UserID):
        self.user_ids = user_ids

    def matches(self, event: EventData) -> bool:
        """ Checks that the event user ID matches any of the user IDs given to the filter. """
        return "user_id" in event and event["user_id"] in self.user_ids


class RoleFilter(BaseFilter):
    """ This filter only matches events that have at least one matching role. """

    def __init__(self, *role_ids: RoleID):
        self.role_ids = set(role_ids)

    def matches(self, event: EventData) -> bool:
        """ Checks that the event roles match at least one of the roles given to the filter. """
        return bool(self.role_ids & event.get("role_ids", set()))


class ReactionFilter(BaseFilter):
    """ This filter only matches events that have at least one matching reaction. """

    def __init__(self, *emoji_ids: ReactionID):
        self.emoji_ids = set(emoji_ids)

    def matches(self, event: EventData) -> bool:
        """ Checks that the event reactions match at least one of the reactions given to the filter. """
        return bool(self.emoji_ids & event.get("emoji_ids", set()))


class MessageFilter(BaseFilter):
    """ This filter only matches events that have at least one matching message. """

    def __init__(self, *message_ids: MessageID):
        self.message_ids = set(message_ids)

    def matches(self, event: EventData) -> bool:
        """ Checks that the event messages match at least one of the messages given to the filter. """
        return bool(self.message_ids & event.get("message_id", set()))
