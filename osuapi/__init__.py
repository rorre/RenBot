import re
from typing import Tuple, Union, List
import aiohttp, urllib

from .User import User
from .Beatmap import Beatmap

MAPSET_REGEX = r'http[s]?:\/\/osu\.ppy\.sh\/([b]?(?:eatmapset)?[s]?)\/([0-9]+)(?:#[a-z]+\/([0-9]+))?'
USERS_REGEX = r'http[s]?:\/\/osu\.ppy\.sh\/u(?:sers)?\/([0-9]*[a-z]*[A-Z]*-*_*%*)'
API_URL = "https://osu.ppy.sh/api/"

class APIWrapper:
    def __init__(self, osu_token):
        self.osu_token = osu_token

    async def get_user(self, uid : Union[int, str]) -> User:
        api_res = await self.fetch_api('get_user', u=str(uid))
        return User(api_res)

    async def get_beatmaps(self, set_id : int) -> List[Beatmap]:
        api_res = await self.fetch_api('get_beatmaps', s=set_id)
        return api_res

    async def fetch_api(self, endpoint, **kwargs):
        kwargs['k'] = self.osu_token
        extras = urllib.parse.urlencode(kwargs)
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL + endpoint + extras) as r:
                if r.status == 200:
                    js = await r.json()
                    return js
                return None

""" Public helper functions """

def get_mapset_ids(msg : str) -> Tuple:
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
    return result.groups()

def get_username(msg : str) -> str:
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
    result_groups = re.search(USERS_REGEX, msg).groups()
    if not result_groups:
        return None
    result = result_groups[0]
    return result