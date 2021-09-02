from typing import Optional, List, Any
from datetime import datetime
from models import (
    from_int, from_bool, from_str, from_list, to_class, from_none,
     from_datetime, from_union
)


class Crew:
    id: Optional[int]
    ready: Optional[bool]
    partner: Optional[str]
    approved: Optional[bool]
    language: Optional[str]
    discord_id: Optional[str]
    discord_tag: Optional[str]
    display_name: Optional[str]
    public_stream: Optional[str]

    def __init__(self, id: Optional[int], ready: Optional[bool], partner: Optional[str], approved: Optional[bool], language: Optional[str], discord_id: Optional[str], discord_tag: Optional[str], display_name: Optional[str], public_stream: Optional[str]) -> None:
        self.id = id
        self.ready = ready
        self.partner = partner
        self.approved = approved
        self.language = language
        self.discord_id = discord_id
        self.discord_tag = discord_tag
        self.display_name = display_name
        self.public_stream = public_stream

    @staticmethod
    def from_dict(obj: Any) -> 'Crew':
        assert isinstance(obj, dict)
        id = from_union([from_int, from_none], obj.get("id"))
        ready = from_union([from_bool, from_none], obj.get("ready"))
        partner = from_union([from_str, from_none], obj.get("partner"))
        approved = from_union([from_bool, from_none], obj.get("approved"))
        language = from_union([from_str, from_none], obj.get("language"))
        discord_id = from_union([from_str, from_none], obj.get("discordId"))
        discord_tag = from_union([from_str, from_none], obj.get("discordTag"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        public_stream = from_union([from_str, from_none], obj.get("publicStream"))
        return Crew(id, ready, partner, approved, language, discord_id, discord_tag, display_name, public_stream)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_int, from_none], self.id)
        result["ready"] = from_union([from_bool, from_none], self.ready)
        result["partner"] = from_union([from_str, from_none], self.partner)
        result["approved"] = from_union([from_bool, from_none], self.approved)
        result["language"] = from_union([from_str, from_none], self.language)
        result["discordId"] = from_union([from_str, from_none], self.discord_id)
        result["discordTag"] = from_union([from_str, from_none], self.discord_tag)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["publicStream"] = from_union([from_str, from_none], self.public_stream)
        return result


class Player:
    id: Optional[int]
    discord_id: Optional[str]
    discord_tag: Optional[str]
    display_name: Optional[str]
    public_stream: Optional[str]
    streaming_from: Optional[str]

    def __init__(self, id: Optional[int], discord_id: Optional[str], discord_tag: Optional[str], display_name: Optional[str], public_stream: Optional[str], streaming_from: Optional[str]) -> None:
        self.id = id
        self.discord_id = discord_id
        self.discord_tag = discord_tag
        self.display_name = display_name
        self.public_stream = public_stream
        self.streaming_from = streaming_from

    @staticmethod
    def from_dict(obj: Any) -> 'Player':
        assert isinstance(obj, dict)
        id = from_union([from_int, from_none], obj.get("id"))
        discord_id = from_union([from_str, from_none], obj.get("discordId"))
        discord_tag = from_union([from_str, from_none], obj.get("discordTag"))
        display_name = from_union([from_str, from_none], obj.get("displayName"))
        public_stream = from_union([from_str, from_none], obj.get("publicStream"))
        streaming_from = from_union([from_str, from_none], obj.get("streamingFrom"))
        return Player(id, discord_id, discord_tag, display_name, public_stream, streaming_from)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_int, from_none], self.id)
        result["discordId"] = from_union([from_str, from_none], self.discord_id)
        result["discordTag"] = from_union([from_str, from_none], self.discord_tag)
        result["displayName"] = from_union([from_str, from_none], self.display_name)
        result["publicStream"] = from_union([from_str, from_none], self.public_stream)
        result["streamingFrom"] = from_union([from_str, from_none], self.streaming_from)
        return result


class SgData:
    players: Optional[List[Player]]
    title: Optional[str]
    commentators: Optional[List[Crew]]
    trackers: Optional[List[Crew]]
    restreamer: Optional[List[Crew]]

    def __init__(self, players: Optional[List[Player]], title: Optional[str], commentators: Optional[List[Crew]], trackers: Optional[List[Crew]], restreamer: Optional[List[Crew]]) -> None:
        self.players = players
        self.title = title
        self.commentators = commentators
        self.trackers = trackers
        self.restreamer = restreamer

    @staticmethod
    def from_dict(obj: Any) -> 'SgData':
        assert isinstance(obj, dict)
        players = from_union([lambda x: from_list(Player.from_dict, x), from_none], obj.get("players"))
        title = from_union([from_str, from_none], obj.get("title"))
        commentators = from_union([lambda x: from_list(Crew.from_dict, x), from_none], obj.get("commentators"))
        trackers = from_union([lambda x: from_list(Crew.from_dict, x), from_none], obj.get("trackers"))
        restreamer = from_union([lambda x: from_list(Crew.from_dict, x), from_none], obj.get("restreamer"))
        return SgData(players, title, commentators, trackers, restreamer)

    def to_dict(self) -> dict:
        result: dict = {}
        result["players"] = from_union([lambda x: from_list(lambda x: to_class(Player, x), x), from_none], self.players)
        result["title"] = from_union([from_str, from_none], self.title)
        result["commentators"] = from_union([lambda x: from_list(lambda x: to_class(Crew, x), x), from_none], self.commentators)
        result["trackers"] = from_union([lambda x: from_list(lambda x: to_class(Crew, x), x), from_none], self.trackers)
        result["restreamer"] = from_union([lambda x: from_list(lambda x: to_class(Crew, x), x), from_none], self.restreamer)
        return result


class RestreamEpisode:
    sg_id: Optional[int]
    channel: Optional[str]
    tracker_prefix: Optional[str]
    keysanity: Optional[int]
    twitch_id: None
    twitch_access: None
    twitch_refresh: None
    sg_data: Optional[SgData]
    last_update: Optional[datetime]

    def __init__(self, sg_id: Optional[int], channel: Optional[str], tracker_prefix: Optional[str], keysanity: Optional[int], twitch_id: None, twitch_access: None, twitch_refresh: None, sg_data: Optional[SgData], last_update: Optional[datetime]) -> None:
        self.sg_id = sg_id
        self.channel = channel
        self.tracker_prefix = tracker_prefix
        self.keysanity = keysanity
        self.twitch_id = twitch_id
        self.twitch_access = twitch_access
        self.twitch_refresh = twitch_refresh
        self.sg_data = sg_data
        self.last_update = last_update

    @staticmethod
    def from_dict(obj: Any) -> 'RestreamEpisode':
        assert isinstance(obj, dict)
        sg_id = from_union([from_int, from_none], obj.get("sg_id"))
        channel = from_union([from_str, from_none], obj.get("channel"))
        tracker_prefix = from_union([from_str, from_none], obj.get("tracker_prefix"))
        keysanity = from_union([from_int, from_none], obj.get("keysanity"))
        twitch_id = from_none(obj.get("twitch_id"))
        twitch_access = from_none(obj.get("twitch_access"))
        twitch_refresh = from_none(obj.get("twitch_refresh"))
        sg_data = from_union([from_none, SgData.from_dict], obj.get("sg_data"))
        last_update = from_union([from_datetime, from_none], obj.get("last_update"))
        return RestreamEpisode(sg_id, channel, tracker_prefix, keysanity, twitch_id, twitch_access, twitch_refresh, sg_data, last_update)

    def to_dict(self) -> dict:
        result: dict = {}
        result["sg_id"] = from_union([from_int, from_none], self.sg_id)
        result["channel"] = from_union([from_str, from_none], self.channel)
        result["tracker_prefix"] = from_union([from_str, from_none], self.tracker_prefix)
        result["keysanity"] = from_union([from_int, from_none], self.keysanity)
        result["twitch_id"] = from_none(self.twitch_id)
        result["twitch_access"] = from_none(self.twitch_access)
        result["twitch_refresh"] = from_none(self.twitch_refresh)
        result["sg_data"] = from_union([lambda x: to_class(SgData, x), from_none], self.sg_data)
        result["last_update"] = from_union([lambda x: x.isoformat(), from_none], self.last_update)
        return result


def episode_from_dict(s: Any) -> RestreamEpisode:
    return RestreamEpisode.from_dict(s)
