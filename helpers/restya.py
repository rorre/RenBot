import aiohttp
import config
from osuapi import APIWrapper, get_mapset_ids, get_username, make_api_kwargs

class RestyaClient:
    def __init__(self, loop=None):
        self.token = None
        self.username = config.restya_username
        self.password = config.restya_password
        self.base_url = config.restya_domain + "/api"
        self.oauth_url = self.base_url + "/v1/oauth.json"
        self.login_url = self.base_url + "/v1/users/login.json"
        self.session = aiohttp.ClientSession(loop=loop)
        self.board_id = config.board_id
        self.list_id = config.list_id

    async def login(self):
        post_data = {
            "email": self.username,
            "password": self.password
        }
        async with self.session.post(self.login_url, json=post_data) as resp:
            js_resp = await resp.json()
            self.token = js_resp['access_token']
        return self.token

    async def add_map(self, beatmap):
        if not self.token: await self.login()
        url = f"{self.base_url}/v1/boards/{self.board_id}/lists/{self.list_id}/cards.json?token={self.token}"
        post_data = {
            "board_id": self.board_id,
            "list_id": self.list_id,
            "name": f"{beatmap.artist} - {beatmap.title} ({beatmap.creator})",
            "position": 0
        }
        async with self.session.post(url, json=post_data) as resp:
            if resp.status == 401:
                await self.login()
                return self.add_map(beatmap)
            json_resp = await resp.json()
            card_id = json_resp['id']

        card_url =  f"{self.base_url}/v1/boards/{self.board_id}/lists/{self.list_id}/cards/{card_id}/attachments.json?token={self.token}"
        cover_url = f"https://assets.ppy.sh/beatmaps/{beatmap.beatmapset_id}/covers/cover@2x.jpg"
        async with self.session.get(cover_url) as cover_resp:
            cover_bytes = await cover_resp.content.read()
        cover_form = aiohttp.FormData()
        cover_form.add_field("attachment", cover_bytes, filename="cover.jpg")
        async with self.session.post(card_url, data=cover_form) as resp:
            if resp.status == 401:
                await self.login()
                return self.add_map(beatmap)
            json_resp = await resp.json()
        return

