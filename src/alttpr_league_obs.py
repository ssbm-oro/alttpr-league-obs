import asyncio
import logging
from threading import Thread
from enum import Enum, auto
import clients.racetime_client as racetime_client
from models.league import RestreamEpisode
import clients.league_client as league_client
from helpers.LogFormatter import LogFormatter
from helpers.obs_context_manager import source_ar, data_ar

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
        channel_list, league_channels.none, league_channels.none)
    obs.obs_property_list_add_string(
        channel_list, league_channels.channel1, league_channels.channel1)
    obs.obs_property_list_add_string(
        channel_list, league_channels.channel2, league_channels.channel2)
    obs.obs_property_list_add_string(
        channel_list, league_channels.channel3, league_channels.channel3)
    obs.obs_property_list_add_string(
        channel_list, league_channels.channel4, league_channels.channel4)
        
    return props


def new_channel_selected(props, prop, settings):
    global curr_restream
    global curr_channel
    obs.timer_remove(update_sources)
    curr_channel = obs.obs_data_get_string(settings, sp.channel)
    print(curr_channel)
    if curr_channel is not league_channels.none:
        curr_restream = league_client.get_restream(curr_channel)
        set_source_text(source_names.left_player, curr_restream.sg_data.players[0].display_name)
        set_source_text(source_names.right_player, curr_restream.sg_data.players[1].display_name)
        set_source_text(source_names.topleft_player, curr_restream.sg_data.players[0].display_name)
        set_source_text(source_names.topright_player, curr_restream.sg_data.players[1].display_name)
        set_source_text(source_names.botleft_player, curr_restream.sg_data.players[2].display_name)
        set_source_text(source_names.botright_player, curr_restream.sg_data.players[3].display_name)
        set_source_text(source_names.left_team, curr_restream.sg_data.players[0].team.team_name)
        set_source_text(source_names.right_team, curr_restream.sg_data.players[1].team.team_name)
        set_image_url(source_names.left_team_logo, curr_restream.sg_data.players[0].team.team_logo)
        set_image_url(source_names.right_team_logo, curr_restream.sg_data.players[1].team.team_logo)
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


def set_image_url(source_name: str, url: str):
    if source_name is None or source_name == "":
        return
    with source_ar(source_name) as source, data_ar() as settings:
        obs.obs_data_set_string(settings, "file", url)
        obs.obs_source_update(source, settings)
