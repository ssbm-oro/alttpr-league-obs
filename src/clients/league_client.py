from typing import Any
import requests

from models.league import episode_from_dict

def script_path():
    pass


base_url = "https://alttprleague.com/api/"

def league_get(uri: str, payload={}):
    headers = {
        'User-Agent': "oro-obs-bot_alpha"
    }
    try:
        with requests.get(uri, payload, headers=headers) as res:
            print(res.status_code)
            if res.status_code == 200:
                print(res.text)
                return res.json()
    except Any:
        return None

def get_restream(channel: str):
    return episode_from_dict(
        league_get(f'{base_url}restream?channel={channel}')
    )