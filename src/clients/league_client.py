from typing import Any
import requests

from models.league import episode_from_dict

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
            if res.status_code == 200:
                return res.json()
    except Any:
        return None

def get_restream(channel: str, token=""):
    return episode_from_dict(
        league_get(f'{base_url}restream?channel={channel}', token=token)
    )