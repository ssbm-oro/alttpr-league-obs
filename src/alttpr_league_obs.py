import asyncio
from datetime import datetime, timedelta, timezone
import pytz
import logging
from threading import Thread
from enum import Enum, auto
import subprocess
from typing import List
import clients.racetime_client as racetime_client
from models.league import CropSettings, Player, RestreamEpisode, SgData, Week
import clients.league_client as league_client
from helpers.LogFormatter import LogFormatter
from helpers.obs_context_manager import scene_ar, scene_list_ar, source_ar, data_ar

import obspython as obs
class script_props(str, Enum):
    channel = auto()
    token = auto()
    refresh_crew_button = auto()
    refresh_countdown_button = auto()
    restart_p1_button = auto()
    restart_p2_button = auto()
    restart_p3_button = auto()
    restart_p4_button = auto()


sp = script_props

class league_channels(str, Enum):
    none = ""
    channel1 = "thealttprleague"
    channel2 = "thealttprleague2"
    channel3 = "thealttprleague3"
    channel4 = "thealttprleague4"

lc = league_channels

class source_names(str, Enum):
    left_player = "Left Name"
    right_player = "Right Name"
    topleft_player = "TL Name"
    topright_player = "TR Name"
    botleft_player = "BL Name"
    botright_player = "BR Name"
    left_team = "Left Team - 2P"
    right_team = "Right Team - 2P"
    crew = "Comm Names"
    crew4p = "Comm Names 4P"
    normal_tracker = "Normal Tracker"
    keys_tracker = "Keysanity Tracker"
    left_team_logo = "L Team Logo"
    right_team_logo = "R Team Logo"
    left_tracker = "Left 1"
    right_tracker = "Right 1"
    topleft_tracker = "TL-1"
    topright_tracker = "TR-1"
    botleft_tracker = "BL-1"
    botright_tracker = "BR-1"
    week_mode = "Week # And Mode"
    countdown = "Time To Match"
    layout_2p = "2P Weekly Layout"
    layout_4p = "4P Weekly layout"
    left_game = "LeftGame"
    left_timer = "LeftTimer"
    right_game = "RightGame"
    right_timer = "RightTimer"
    tl_game = "LeftGame"
    tl_timer = "LeftTimer"
    tr_game = "RightGame"
    tr_timer = "RightTimer"
    bl_game = "BLGame"
    bl_timer = "BLTimer"
    br_game = "BRGame"
    br_timer = "BRTimer"
    scedule_time = "Schedule Time"


class scene_names(str, Enum):
    intro = "Intro"
    two_player = "2P"
    four_player = "4P"
    outro = "Outro"

sc_n = scene_names

tracker_url = (
    "https://lttp-tracker-tournament-only.firebaseapp.com/"
    "{tracker_prefix}{side}?password={password}&keysanity={keysanity}"
    "&layout={layout}"
)

sn = source_names

curr_channel: str = league_channels.none
curr_restream: RestreamEpisode = None
logger = logging.Logger("alttpr-league-obs")
logger.setLevel(logging.INFO)
logger.handlers.clear()
handler = logging.StreamHandler()
handler.setFormatter(LogFormatter())
logger.disabled = False
logger.info("started")
streams = []
api_token = ""
channel_list = None
refresh_crew_button = None
restart_p1_button = None
restart_p2_button = None
restart_p3_button = None
restart_p4_button = None
token_textbox = None
race_started_at : datetime = None


def script_description():
    message = (
        "Select which channel you are broadcasting to load all pertinent data."
    )
    return (
        "<center>alttpr-league-obs xxVERSIONxx<hr>"
        "<p>" + message + "<hr/></p>"
    )


def script_load(settings):
    obs.obs_frontend_add_event_callback(on_load)
    obs.obs_data_set_string(settings, sp.channel, lc.none)


def on_load(event):
    if event == obs.OBS_FRONTEND_EVENT_FINISHED_LOADING:
        pass
    if event == obs.OBS_FRONTEND_EVENT_EXIT:
        save_crop(curr_restream.sg_data.players, curr_restream.week.coop)
        close_streams()
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTING:
        if channel_list:
            obs.obs_property_set_enabled(channel_list, False)
        if token_textbox:
            obs.obs_property_set_enabled(token_textbox, False)
        pass
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        if (refresh_crew_button):
            obs.obs_property_set_enabled(refresh_crew_button, True)
        pass
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPING:
        if (refresh_crew_button):
            obs.obs_property_set_enabled(refresh_crew_button, False)
        pass
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED:
        if channel_list:
            obs.obs_property_set_enabled(channel_list, True)
        if token_textbox:
            obs.obs_property_set_enabled(token_textbox, True)
    return True


def script_update(settings):
    channel = obs.obs_data_get_string(settings, sp.channel)
    global api_token
    api_token = obs.obs_data_get_string(settings, sp.token)


def script_properties():
    props = obs.obs_properties_create()
    global channel_list
    channel_list = obs.obs_properties_add_list(
        props, sp.channel, "Channel",
        obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING
        )
    obs.obs_property_set_modified_callback(
        channel_list, new_channel_selected
    )
    obs.obs_property_list_add_string(
        channel_list, lc.none, lc.none)
    obs.obs_property_list_add_string(channel_list, lc.channel1, lc.channel1)
    obs.obs_property_list_add_string(channel_list, lc.channel2, lc.channel2)
    obs.obs_property_list_add_string(channel_list, lc.channel3, lc.channel3)
    obs.obs_property_list_add_string(channel_list, lc.channel4, lc.channel4)

    global token_textbox
    token_textbox = obs.obs_properties_add_text(props, sp.token, "API Token", obs.OBS_TEXT_PASSWORD)

    refresh_countdown = obs.obs_properties_add_button(
        props, sp.refresh_countdown_button, "Refresh Countdown",
        lambda *props: None
    )
    obs.obs_property_set_modified_callback(
        refresh_countdown, refresh_countdown_pressed
    )


    global refresh_crew_button
    refresh_crew_button = obs.obs_properties_add_button(
        props, sp.refresh_crew_button, "Refresh Crew", lambda *props: None)
    obs.obs_property_set_modified_callback(
        refresh_crew_button, refresh_crew_pressed)
    obs.obs_property_set_enabled(refresh_crew_button, False)

    global restart_p1_button
    global restart_p2_button
    global restart_p3_button
    global restart_p4_button

    restart_p1_button = obs.obs_properties_add_button(
        props, sp.restart_p1_button, "Restart Left/TopLeft Stream", lambda *props: None)
    obs.obs_property_set_modified_callback(
        restart_p1_button, restart_p1_pressed)
    obs.obs_property_set_enabled(restart_p1_button, False)

    restart_p2_button = obs.obs_properties_add_button(
        props, sp.restart_p2_button, "Restart Right/TopRight Stream", lambda *props: None)
    obs.obs_property_set_modified_callback(
        restart_p2_button, restart_p2_pressed)
    obs.obs_property_set_enabled(restart_p2_button, False)

    restart_p3_button = obs.obs_properties_add_button(
        props, sp.restart_p3_button, "Restart BottomLeft Stream", lambda *props: None)
    obs.obs_property_set_modified_callback(
        restart_p3_button, restart_p3_pressed)
    obs.obs_property_set_enabled(restart_p3_button, False)

    restart_p4_button = obs.obs_properties_add_button(
        props, sp.restart_p4_button, "Restart BottomRight Stream", lambda *props: None)
    obs.obs_property_set_modified_callback(
        restart_p4_button, restart_p4_pressed)
    obs.obs_property_set_enabled(restart_p4_button, False)
        
    return props

def restart_p1_pressed(props, prop, *arg, **kwargs):
    restart_stream(curr_restream.sg_data.players, 0)

def restart_p2_pressed(props, prop, *arg, **kwargs):
    restart_stream(curr_restream.sg_data.players, 1)

def restart_p3_pressed(props, prop, *arg, **kwargs):
    restart_stream(curr_restream.sg_data.players, 2)

def restart_p4_pressed(props, prop, *arg, **kwargs):
    restart_stream(curr_restream.sg_data.players, 3)

def restart_stream(players: List[Player], index: int):
    if len(streams) > index:
        if streams[index]:
            streams[index].kill()
        streams[index] = subprocess.Popen(
            get_streamlink_command(players, index)
        )


def refresh_crew_pressed(props, prop, *arg, **kwargs):
    if curr_channel != league_channels.none:
        curr_restream = league_client.get_restream(curr_channel, token=api_token)
        if (curr_restream and curr_restream.sg_data):
            update_crew(curr_restream)

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, sp.channel, lc.none)


def new_channel_selected(props, prop, settings):
    global curr_restream
    global curr_channel
    close_streams()
    obs.timer_remove(update_countdown)
    curr_channel = obs.obs_data_get_string(settings, sp.channel)
    print(curr_channel)
    if curr_channel != league_channels.none:
        curr_restream = league_client.get_restream(curr_channel, token=api_token)
        if (curr_restream and curr_restream.sg_data):
            if curr_restream.twitch_stream_key:
                set_stream_key(curr_restream.twitch_stream_key)
            players = curr_restream.sg_data.players

            if curr_restream.sg_data is not None:
                obs.timer_add(update_countdown, 100)

            update_intro(curr_restream.week, curr_restream.sg_data.match_time)
            update_players(players, True)
            update_teams(players)
            update_trackers(curr_restream)
            update_crew(curr_restream)
            update_layout(curr_restream)

            update_racetime(curr_restream.rtgg_slug)

    return True

def refresh_countdown_pressed(props, prop, *arg, **args):
    if curr_channel != league_channels.none:
        restream = league_client.get_restream(curr_channel, token=api_token)
        update_racetime(restream.rtgg_slug)
    pass

def update_racetime(rtgg_slug: str):
    if rtgg_slug:
        race = racetime_client.get_race_by_name(rtgg_slug)
        if race.started_at:
            global race_started_at
            race_started_at = race.started_at

def update_layout(restream: RestreamEpisode):
    if restream is not None and restream.sg_data is not None:
        if restream.week is not None:
            week_no = restream.week.event[-1]
            path = f"./../../../layouts/League_Season4-Open-week{week_no}.png"
            if restream.sg_data.is_invitational:                
                path = f"./../../../layouts/League_Season4-week{week_no}.png"
            if restream.week.coop:
                set_source_file(sn.layout_4p, path)
            else:
                set_source_file(sn.layout_2p, path)

def update_intro(week: Week, match_time: datetime):
    if week:
        set_source_text(sn.week_mode, f"{week.event}: {week.mode_name}")
    if match_time is not None:
        set_source_text(
            sn.scedule_time,
            match_time.astimezone(pytz.timezone('US/Eastern')).strftime("%B %d %Y %I:%M %p")
        )

def update_players(players: List[Player], start_streams: bool = False):
    global streams

    global restart_p1_button
    global restart_p2_button
    global restart_p3_button
    global restart_p4_button

    set_source_text(sn.left_player, players[0].player_name)
    set_source_text(sn.right_player, players[1].player_name)
    if start_streams:
        streams.append(subprocess.Popen(get_streamlink_command(players, 0)))
        obs.obs_property_set_enabled(restart_p1_button, True)
        streams.append(subprocess.Popen(get_streamlink_command(players, 1)))
        obs.obs_property_set_enabled(restart_p2_button, True)
    set_source_text(sn.topleft_player, players[0].player_name)
    if players[0].crop is not None:
        set_crop_settings(players[0].crop, sc_n.two_player, sn.left_game, sn.left_timer)
    if players[1].crop is not None:
        set_crop_settings(players[1].crop, sc_n.two_player, sn.right_game, sn.right_timer)
    set_source_text(sn.topright_player, players[1].player_name)
    if (len(players) > 2):
        set_source_text(sn.left_player, f"{players[0].player_name}, {players[2].player_name}")
        set_source_text(sn.right_player, f"{players[1].player_name}, {players[3].player_name}")

        if players[0].crop is not None:
            set_crop_settings(players[0].crop, sc_n.four_player, sn.tl_game, sn.tl_timer)
        if players[1].crop is not None:
            set_crop_settings(players[1].crop, sc_n.four_player, sn.tr_game, sn.tr_timer)
        if players[2].crop is not None:
            set_crop_settings(players[2].crop, sc_n.four_player, sn.bl_game, sn.bl_timer)
        if players[3].crop is not None:
            set_crop_settings(players[3].crop, sc_n.four_player, sn.br_game, sn.br_timer)

        set_source_text(sn.topright_player, players[1].player_name)
        set_source_text(sn.botleft_player, players[2].player_name)
        set_source_text(sn.botright_player, players[3].player_name)
        if start_streams:
            streams.append(subprocess.Popen(get_streamlink_command(players, 2)))
            obs.obs_property_set_enabled(restart_p3_button, True)
            streams.append(subprocess.Popen(get_streamlink_command(players, 3)))
            obs.obs_property_set_enabled(restart_p4_button, True)

def update_trackers(restream: RestreamEpisode):
    if restream.week.coop:
        set_source_url(sn.topleft_tracker, restream.sg_data.players[0].tracker)
        set_source_url(sn.topright_tracker, restream.sg_data.players[1].tracker)
        set_source_url(sn.botleft_tracker, restream.sg_data.players[2].tracker)
        set_source_url(sn.botright_tracker, restream.sg_data.players[3].tracker)
    else:
        set_source_url(sn.left_tracker, restream.sg_data.players[0].tracker)
        set_source_url(sn.right_tracker, restream.sg_data.players[1].tracker)

def update_teams(players):
    l_team = players[0].team
    r_team = players[1].team
    set_source_text(sn.left_team, f"{l_team.team_name} - {l_team.points}")
    set_source_text(sn.right_team, f"{r_team.team_name} - {r_team.points}")
    set_source_file(sn.left_team_logo, l_team.team_logo)
    set_source_file(sn.right_team_logo, r_team.team_logo)

def update_crew(restream: RestreamEpisode):
    comms = "C: "
    for comm in restream.sg_data.commentators[:-1]:
        print(comm)
        comms += f"{comm.display_name}, "
    if len(restream.sg_data.commentators) > 0:
        comms += f"{restream.sg_data.commentators[-1].display_name}"

    trackers = "T: "
    for tracker in restream.sg_data.trackers[:-1]:
        trackers += f"{tracker.display_name}, "
    if len(restream.sg_data.trackers) > 0:
        trackers += f"{restream.sg_data.trackers[-1].display_name}"

    set_source_text(sn.crew, f"{comms} {trackers}")
    print(f"{comms} {trackers}")
    set_source_text(sn.crew4p, f"{comms}\n{trackers}")
    print(f"{comms}\n{trackers}")

def update_countdown():
    start_time :datetime
    if curr_restream.sg_data is not None:
        if curr_restream.week.spoiler:
            start_time = curr_restream.sg_data.match_time
        else:
            start_time = curr_restream.sg_data.match_time - timedelta(minutes=10)
    if race_started_at is not None:
        start_time = race_started_at

    timer : timedelta
    if curr_restream.week.spoiler:
        timer = datetime.now(timezone.utc) - start_time
    else:
        timer = datetime.now(timezone.utc) - start_time - timedelta(minutes=10)
    time = timer_to_str(timer)
    set_source_text(sn.countdown, time)


def timer_to_str(timer: timedelta, decimals: bool = True) -> str:
    substring = 9
    if not decimals:
        substring = 7
    if timer.total_seconds() < 0.0:
        timer = timer * -1.0
        return "-" + str(timer)[:substring]
    return str(timer)[:substring]


def set_source_text(source_name: str, text: str):
    if source_name is None or source_name == "":
        return
    with source_ar(source_name) as source, data_ar() as settings:
        obs.obs_data_set_string(settings, "text", text)
        obs.obs_source_update(source, settings)


def set_source_file(source_name: str, url: str):
    if source_name is None or source_name == "":
        return
    with source_ar(source_name) as source, data_ar() as settings:
        obs.obs_data_set_string(settings, "file", url)
        obs.obs_source_update(source, settings)

def set_source_url(source_name: str, url: str):
    if source_name is None or source_name == "":
        return
    with source_ar(source_name) as source, data_ar() as settings:
        obs.obs_data_set_string(settings, "url", url)
        obs.obs_source_update(source, settings)


def set_source_visibility(scene_name: str, source_name: str, vis: bool):
    if (scene_name is None or scene_name == "" or
        source_name is None or source_name == ""):
        return
    with scene_ar(scene_name) as scene, data_ar() as settings:
        source = obs.obs_scene_find_source(scene, source_name)
        obs.obs_sceneitem_set_visible(source, vis)


def get_streamlink_command(players: List[Player], i: int):
    port = 27770 + i
    return ["streamlink.exe", f"https://twitch.tv/{players[i].twitch_url}",
        "best", "--player-external-http", "--player-external-http-port",
        str(port), "--twitch-disable-ads", "--twitch-disable-hosting",
        "--twitch-disable-reruns", "--retry-streams", "5"]

def close_streams():
    for stream in streams:
            stream.kill()
    streams.clear()


def set_stream_key(stream_key: str):
    service = obs.obs_frontend_get_streaming_service()
    if (service is None):
        return
    settings = obs.obs_service_get_settings(service)
    obs.obs_data_set_string(settings, "key", stream_key)
    obs.obs_service_update(service, settings)
    obs.obs_data_release(settings)
    obs.obs_frontend_save_streaming_service()

def save_crop(players: List[Player], coop: bool):
    if coop:
        tl_crop = get_crop_settings(scene_names.four_player, sn.tl_game, sn.tl_timer)
        print(league_client.post_crop(players[0].player_id, tl_crop, token=api_token))
        tr_crop = get_crop_settings(scene_names.four_player, sn.tr_game, sn.tr_timer)
        print(league_client.post_crop(players[1].player_id, tr_crop, token=api_token))
        bl_crop = get_crop_settings(scene_names.four_player, sn.bl_game, sn.bl_timer)
        print(league_client.post_crop(players[2].player_id, bl_crop, token=api_token))
        br_crop = get_crop_settings(scene_names.four_player, sn.br_game, sn.br_timer)
        print(league_client.post_crop(players[3].player_id, br_crop, token=api_token))
    else:
        left_crop = get_crop_settings(sc_n.two_player, sn.left_game, sn.left_timer)
        print(league_client.post_crop(players[0].player_id, left_crop, token=api_token))
        right_crop = get_crop_settings(sc_n.two_player, sn.right_game, sn.right_timer)
        print(league_client.post_crop(players[1].player_id, right_crop, token=api_token))

def get_crop_settings(scene_name: str, game_source_name: str, timer_source_name: str):
    if (
        scene_name is None or scene_name == "" or 
        game_source_name is None or game_source_name == "" or
        timer_source_name is None or timer_source_name == ""
    ):
        return
    with scene_list_ar() as scenes:
        for scene in scenes:
            name = obs.obs_source_get_name(scene)
            if name == scene_name:
                scene = obs.obs_scene_from_source(scene)
                game_source = obs.obs_scene_find_source_recursive(scene, game_source_name)
                timer_source = obs.obs_scene_find_source_recursive(scene, timer_source_name)
                if game_source and timer_source:
                    game_crop = obs.obs_sceneitem_crop()
                    obs.obs_sceneitem_get_crop(game_source, game_crop)
                    timer_crop = obs.obs_sceneitem_crop()
                    obs.obs_sceneitem_get_crop(timer_source, timer_crop)
                    return(
                        CropSettings(
                            game_crop.top, game_crop.left,
                            game_crop.right, game_crop.bottom,
                            timer_crop.top, timer_crop.left,
                            timer_crop.right, timer_crop.bottom
                        )
                    )

def set_crop_settings(settings: CropSettings, scene_name: str, game_source_name: str, timer_source_name: str):
    if (
        settings is None or 
        scene_name is None or scene_name == "" or 
        game_source_name is None or game_source_name == "" or
        timer_source_name is None or timer_source_name == ""
    ):
        return
    
    with scene_list_ar() as scenes:
        for scene in scenes:
            name = obs.obs_source_get_name(scene)
            if name == scene_name:
                scene = obs.obs_scene_from_source(scene)
                game_source = obs.obs_scene_find_source_recursive(scene, game_source_name)
                timer_source = obs.obs_scene_find_source_recursive(scene, timer_source_name)
                if game_source and timer_source:
                    game_crop = obs.obs_sceneitem_crop()
                    game_crop.top = settings.game_top
                    game_crop.bottom = settings.game_bottom
                    game_crop.left = settings.game_left
                    game_crop.right = settings.game_right
                    obs.obs_sceneitem_set_crop(game_source, game_crop)
                    timer_crop = obs.obs_sceneitem_crop()
                    timer_crop.top = settings.timer_top
                    timer_crop.bottom = settings.timer_bottom
                    timer_crop.left = settings.timer_left
                    timer_crop.right = settings.timer_right
                    obs.obs_sceneitem_set_crop(timer_source, timer_crop)
    