from typing import Any, List
from datetime import datetime
from models import (
    from_int, from_bool, from_str, from_list, to_class, from_none,
     from_datetime
)


class Crew:
    id: int
    ready: bool
    partner: str
    approved: bool
    language: str
    discord_id: str
    discord_tag: str
    display_name: str
    public_stream: str

    def __init__(self, id: int, ready: bool, partner: str, approved: bool, language: str, discord_id: str, discord_tag: str, display_name: str, public_stream: str) -> None:
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
        id = from_int(obj.get("id"))
        ready = from_bool(obj.get("ready"))
        partner = from_str(obj.get("partner"))
        approved = from_bool(obj.get("approved"))
        language = from_str(obj.get("language"))
        discord_id = from_str(obj.get("discordId"))
        discord_tag = from_str(obj.get("discordTag"))
        display_name = from_str(obj.get("displayName"))
        public_stream = from_str(obj.get("publicStream"))
        return Crew(id, ready, partner, approved, language, discord_id, discord_tag, display_name, public_stream)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["ready"] = from_bool(self.ready)
        result["partner"] = from_str(self.partner)
        result["approved"] = from_bool(self.approved)
        result["language"] = from_str(self.language)
        result["discordId"] = from_str(self.discord_id)
        result["discordTag"] = from_str(self.discord_tag)
        result["displayName"] = from_str(self.display_name)
        result["publicStream"] = from_str(self.public_stream)
        return result


class Player:
    id: int
    discord_id: str
    discord_tag: str
    display_name: str
    public_stream: str
    streaming_from: str

    def __init__(self, id: int, discord_id: str, discord_tag: str, display_name: str, public_stream: str, streaming_from: str) -> None:
        self.id = id
        self.discord_id = discord_id
        self.discord_tag = discord_tag
        self.display_name = display_name
        self.public_stream = public_stream
        self.streaming_from = streaming_from

    @staticmethod
    def from_dict(obj: Any) -> 'Player':
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        discord_id = from_str(obj.get("discordId"))
        discord_tag = from_str(obj.get("discordTag"))
        display_name = from_str(obj.get("displayName"))
        public_stream = from_str(obj.get("publicStream"))
        streaming_from = from_str(obj.get("streamingFrom"))
        return Player(id, discord_id, discord_tag, display_name, public_stream, streaming_from)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["discordId"] = from_str(self.discord_id)
        result["discordTag"] = from_str(self.discord_tag)
        result["displayName"] = from_str(self.display_name)
        result["publicStream"] = from_str(self.public_stream)
        result["streamingFrom"] = from_str(self.streaming_from)
        return result


class SgData:
    players: List[Player]
    title: str
    commentators: List[Crew]
    trackers: List[Crew]
    restreamer: List[Crew]

    def __init__(self, players: List[Player], title: str, commentators: List[Crew], trackers: List[Crew], restreamer: List[Crew]) -> None:
        self.players = players
        self.title = title
        self.commentators = commentators
        self.trackers = trackers
        self.restreamer = restreamer

    @staticmethod
    def from_dict(obj: Any) -> 'SgData':
        assert isinstance(obj, dict)
        players = from_list(Player.from_dict, obj.get("players"))
        title = from_str(obj.get("title"))
        commentators = from_list(Crew.from_dict, obj.get("commentators"))
        trackers = from_list(Crew.from_dict, obj.get("trackers"))
        restreamer = from_list(Crew.from_dict, obj.get("restreamer"))
        return SgData(players, title, commentators, trackers, restreamer)

    def to_dict(self) -> dict:
        result: dict = {}
        result["players"] = from_list(lambda x: to_class(Player, x), self.players)
        result["title"] = from_str(self.title)
        result["commentators"] = from_list(lambda x: to_class(Crew, x), self.commentators)
        result["trackers"] = from_list(lambda x: to_class(Crew, x), self.trackers)
        result["restreamer"] = from_list(lambda x: to_class(Crew, x), self.restreamer)
        return result


class RestreamEpisode:
    sg_id: int
    channel: str
    tracker_prefix: str
    keysanity: int
    twitch_id: None
    twitch_access: None
    twitch_refresh: None
    sg_data: SgData
    last_update: datetime

    def __init__(self, sg_id: int, channel: str, tracker_prefix: str, keysanity: int, twitch_id: None, twitch_access: None, twitch_refresh: None, sg_data: SgData, last_update: datetime) -> None:
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
        sg_id = from_int(obj.get("sg_id"))
        channel = from_str(obj.get("channel"))
        tracker_prefix = from_str(obj.get("tracker_prefix"))
        keysanity = from_int(obj.get("keysanity"))
        twitch_id = from_none(obj.get("twitch_id"))
        twitch_access = from_none(obj.get("twitch_access"))
        twitch_refresh = from_none(obj.get("twitch_refresh"))
        sg_data = SgData.from_dict(obj.get("sg_data"))
        last_update = from_datetime(obj.get("last_update"))
        return RestreamEpisode(sg_id, channel, tracker_prefix, keysanity, twitch_id, twitch_access, twitch_refresh, sg_data, last_update)

    def to_dict(self) -> dict:
        result: dict = {}
        result["sg_id"] = from_int(self.sg_id)
        result["channel"] = from_str(self.channel)
        result["tracker_prefix"] = from_str(self.tracker_prefix)
        result["keysanity"] = from_int(self.keysanity)
        result["twitch_id"] = from_none(self.twitch_id)
        result["twitch_access"] = from_none(self.twitch_access)
        result["twitch_refresh"] = from_none(self.twitch_refresh)
        result["sg_data"] = to_class(SgData, self.sg_data)
        result["last_update"] = self.last_update.isoformat()
        return result


def episode_from_dict(s: Any) -> RestreamEpisode:
    return RestreamEpisode.from_dict(s)