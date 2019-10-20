import re
from typing import Tuple
import aiohttp, urllib

MAPSET_REGEX = r'http[s]?:\/\/osu.ppy.sh\/([b]?.*[s]?)\/([0-9]+)#[a-z]+\/([0-9]+)'
USERS_REGEX = r'http[s]?:\/\/osu.ppy.sh\/u.*\/([0-9]*)'
API_URL = "https://osu.ppy.sh/api/"

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

def get_uid(msg : str) -> int:
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
    if not result.isdigit():
        api_res = await fetch_api('get_user', u=result)
        if not api_res:
            return None
        result = api_res[0]['user_id']
    return result

async def fetch_api(endpoint, **kwargs):
    extras = urllib.parse.urlencode(kwargs)
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL + endpoint + kwargs) as r:
            if r.status == 200:
                js = await r.json()
                return js
            return None

