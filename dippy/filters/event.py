from dataclasses import dataclass, field
from typing import Optional, Set


GuildID = int
ChannelID = int
RoleID = int
UserID = int
Label = str


@dataclass
class Event:
    guild_id: Optional[GuildID] = None
    channel_id: Optional[ChannelID] = None
    role_ids: Set[RoleID] = field(default_factory=set)
    member_id: Optional[UserID] = None
    labels: Set[Label] = field(default_factory=set)
