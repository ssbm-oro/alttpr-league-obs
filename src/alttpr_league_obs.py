import asyncio
import logging
from threading import Thread
from enum import Enum, auto
import clients.racetime_client as racetime_client
from models.league import RestreamEpisode
import clients.league_client as league_client
from helpers.LogFormatter import LogFormatter
from helpers.obs_context_manager import scene_ar, source_ar, data_ar

import obspython as obs

class script_props(str, Enum):
    channel = auto()

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
    comms = "Comm Names"
    normal_tracker = "Normal Tracker"
    keys_tracker = "Keysanity Tracker"
    left_team_logo = "L Team Temp"
    right_team_logo = "R Team Temp"
    left_tracker = "Left 1"
    right_tracker = "Right 1"
    topleft_tracker = "TL-1"
    topright_tracker = "TR-1"
    botleft_tracker = "BL-1"
    botright_tracker = "BR-1"


class scene_names(str, Enum):
    intro = "Intro"
    two_player = "2P"
    four_player = "4P"
    outro = "Outro"

tracker_url = (
    "https://lttp-tracker-tournament-only.firebaseapp.com/"
    "{tracker_prefix}{side}?password={password}&keysanity={keysanity}"
    "&layout={layout}"
)

sn = source_names


curr_channel: str = league_channels.none
curr_restream: RestreamEpisode = None
logger = logging.Logger("alttpr-ladder-obs")
logger.setLevel(logging.INFO)
logger.handlers.clear()
handler = logging.StreamHandler()
handler.setFormatter(LogFormatter())
logger.disabled = False
logger.info("started")


def script_description():
    message = (
        "Select which channel you are broadcasting to load all pertinent data."
    )
    return (
        "<center>alttpr-ladder-obs xxVERSIONxx<hr>"
        "<p>" + message + "<hr/></p>"
    )


def script_load(settings):
    obs.obs_frontend_add_event_callback(on_load)
    obs.obs_data_set_string(settings, sp.channel, lc.none)


def on_load(event):
    if event == obs.OBS_FRONTEND_EVENT_FINISHED_LOADING:
        pass


def script_update(settings):
    channel = obs.obs_data_get_string(settings, sp.channel)


def script_properties():
    props = obs.obs_properties_create()
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
        
    return props


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, sp.channel, lc.none)


def new_channel_selected(props, prop, settings):
    global curr_restream
    global curr_channel
    obs.timer_remove(update_sources)
    curr_channel = obs.obs_data_get_string(settings, sp.channel)
    print(curr_channel)
    if curr_channel != league_channels.none:
        curr_restream = league_client.get_restream(curr_channel)
        if (curr_restream and curr_restream.sg_data):
            players = curr_restream.sg_data.players
            set_source_text(sn.left_player, players[0].display_name)
            set_source_text(sn.right_player, players[1].display_name)
            set_source_text(sn.topleft_player, players[0].display_name)
            set_source_text(sn.topright_player, players[1].display_name)
            if (len(players) > 2):
                set_source_text(sn.botleft_player, players[2].display_name)
                set_source_text(sn.botright_player, players[3].display_name)
            set_source_text(sn.left_team, players[0].team.team_name)
            set_source_text(sn.right_team, players[1].team.team_name)
            set_source_file(sn.left_team_logo, players[0].team.team_logo)
            set_source_file(sn.right_team_logo, players[1].team.team_logo)

            keys = curr_restream.keysanity == 1

            left_tracker_url = str.format(
                tracker_url, tracker_prefix=curr_restream.tracker_prefix,
                side="left", password="league1",
                keysanity=keys, layout="2"
            )
            print(left_tracker_url)
            set_source_url(sn.left_tracker, left_tracker_url)
            right_tracker_url = str.format(
                tracker_url, tracker_prefix=curr_restream.tracker_prefix,
                side="right", password="league1",
                keysanity=keys, layout="2"
            )
            print(right_tracker_url)
            set_source_url(sn.right_tracker, right_tracker_url)
        if curr_restream is not None:
            obs.timer_add(update_sources, 100)

def update_sources():
    pass


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