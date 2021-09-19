from typing import Any
import requests

from models.league import CropSettings, episode_from_dict

def script_path():
    pass


base_url = "https://alttprleague.com/api/"

def league_get(uri: str, payload={}, token=""):
    headers = {
        'User-Agent': "oro-obs-bot_alpha",
        'Authentication': token
    }
    try:
        with requests.get(uri, payload, headers=headers) as res:
            print(res.status_code)
            print(res.text)
            if res.status_code == 200:
                return res.json()
    except Any:
        return None

def league_post(uri: str, payload={}, token=""):
    headers = {
        'User-Agent': "oro-obs-bot_alpha",
        'Authentication': token
    }
    try:
        with requests.post(uri, data=payload, headers=headers) as res:
            if res.status_code == 204:
                return True
            else:
                return False
    except Any:
        return False


def get_restream(channel: str, token=""):
    return episode_from_dict(
        league_get(f'{base_url}restream?channel={channel}', token=token)
    )


def post_crop(id: int, crop_settings: CropSettings, token=""):
    return league_post(
        f'{base_url}crop?id={id}',
        payload=crop_settings.to_dict(),
        token=token
    )
