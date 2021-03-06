import re
import urllib
from typing import List, Tuple, Union

import aiohttp

from .Beatmap import Beatmap
from .User import User

MAPSET_REGEX = r'http[s]?:\/\/osu\.ppy\.sh\/([b]?(?:eatmapset)?[s]?)\/([0-9]+)(?:#[a-z]+\/([0-9]+))?'
USERS_REGEX = r'http[s]?:\/\/osu\.ppy\.sh\/u(?:sers)?\/([-\[\]\w]*)'
API_URL = "https://osu.ppy.sh/api/"


class APIWrapper:
    def __init__(self, osu_token):
        self.osu_token = osu_token

    async def get_users(self, uid: Union[int, str]) -> List[User]:
        api_res = await self.fetch_api('get_user', u=str(uid))
        return [User(res) for res in api_res]

    async def get_beatmaps(self, **kwargs) -> List[Beatmap]:
        api_res = await self.fetch_api('get_beatmaps', **kwargs)
        return [Beatmap(map) for map in api_res]

    async def fetch_api(self, endpoint, **kwargs):
        kwargs['k'] = self.osu_token
        extras = '?' + urllib.parse.urlencode(kwargs)
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL + endpoint + extras) as r:
                if r.status == 200:
                    js = await r.json()
                    return js
                return None


""" Public helper functions """


def get_mapset_ids(msg: str) -> Tuple:
    """Get mapset URL from message and extract id

    Parameters
    ----------
    msg : str
        Message to check

    Returns
    -------
    tuple of str
        Tuple of ('type', 'beatmapset id', 'beatmap id')
    """
    result = re.search(MAPSET_REGEX, msg)
    if not result:
        return None
    return result.groups()


def get_username(msg: str) -> str:
    """Get osu! user id from message

    Parameters
    ----------
    msg : str
        Message to check

    Returns
    -------
    int
        User ID from message gathered
    """
    result = re.search(USERS_REGEX, msg)
    if not result:
        return None
    result_groups = result.groups()
    if not result_groups:
        return None
    result = result_groups[0]
    return result


def make_api_kwargs(regex_res):
    kwargs = {}
    if regex_res[0] in ['s', 'beatmapsets']:
        kwargs['s'] = regex_res[1]
    else:
        kwargs['b'] = regex_res[1]
    return kwargs
