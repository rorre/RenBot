# -*- coding: utf-8 -*-

import asyncio
from typing import Optional

import discord
from discord.ext import commands

import config
from helpers import db, embeds
from osuapi import APIWrapper, get_mapset_ids, get_username, make_api_kwargs

def check_channel(ctx):
    return ctx.message.channel.id == config.modreqs_channel

class OwnerCommands(commands.Cog):
    """Owner only commands."""
    qualified_name = "Owner"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["r", "req"])
    @commands.guild_only()
    @commands.check(check_channel)
    async def request(self, ctx, map_url: str):
        """Requests a mod"""
        print(f"[request] Getting osu!map url")
        set_regex = get_mapset_ids(map_url)

        if not set_regex:
            await ctx.send("Please send valid beatmap!")
            return

        kwargs = make_api_kwargs(set_regex)
        maps = await self.bot.osu_client.get_beatmaps(**kwargs)
        if not maps:
            return ctx.send("No map found with that URL.")

        print("[request] Adding map to restya")
        await self.bot.restya_client.add_map(maps[0])
        await ctx.send("Sent!")



def setup(bot):
    bot.add_cog(OwnerCommands(bot))
