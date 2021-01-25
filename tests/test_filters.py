from dippy.filters.filters import (
    LabelFilter,
    GlobalFilter,
    RoleFilter,
    ChannelFilter,
    UserFilter,
    GuildFilter,
)


class TestFilters:
    def test_inverse_filter(self):
        f = ~GuildFilter(123456)
        e = dict(guild_id=123456)
        assert not f.matches(e)

    def test_aggregate_or_filter(self):
        f = GuildFilter(123456) | GuildFilter(654321)
        e1 = dict(guild_id=123456)
        e2 = dict(guild_id=654321)
        e3 = dict(guild_id=567890)
        assert f.matches(e1)
        assert f.matches(e2)
        assert not f.matches(e3)

    def test_aggregate_and_filter(self):
        f = GuildFilter(123456) & ChannelFilter(654321)
        e1 = dict(guild_id=123456, channel_id=654321)
        e2 = dict(guild_id=654321)
        e3 = dict(guild_id=567890, channel_id=654321)
        assert f.matches(e1)
        assert not f.matches(e2)
        assert not f.matches(e3)

    def test_global_filter(self):
        assert GlobalFilter().matches(dict())

    def test_label_filter(self):
        f1 = LabelFilter("testing")
        f2 = LabelFilter("testing", "test")
        assert f1.matches(dict(labels={"testing"}))
        assert not f1.matches(dict(labels={"test"}))
        assert f2.matches(dict(labels={"testing"}))
        assert f2.matches(dict(labels={"test"}))
        assert f2.matches(dict(labels={"test", "testing"}))
        assert f2.matches(dict(labels={"test", "foobar"}))
        assert not f2.matches(dict(labels={"foobar"}))

    def test_guild_filter(self):
        f = GuildFilter(123456789, 987654321)
        assert f.matches(dict(guild_id=123456789))
        assert f.matches(dict(guild_id=987654321))
        assert not f.matches(dict(guild_id=123456))

    def test_channel_filter(self):
        f = ChannelFilter(123456789, 987654321)
        assert f.matches(dict(channel_id=123456789))
        assert f.matches(dict(channel_id=987654321))
        assert not f.matches(dict(channel_id=123456))

    def test_user_filter(self):
        f = UserFilter(123456789, 987654321)
        assert f.matches(dict(user_id=123456789))
        assert f.matches(dict(user_id=987654321))
        assert not f.matches(dict(user_id=123456))

    def test_role_filter(self):
        f = RoleFilter(1, 2)
        assert f.matches(dict(role_ids={1}))
        assert f.matches(dict(role_ids={2}))
        assert f.matches(dict(role_ids={1, 2}))
        assert f.matches(dict(role_ids={1, 3}))
        assert not f.matches(dict(role_ids={3}))
