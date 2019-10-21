#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
from typing import Optional
import discord
import config
from osuapi import APIWrapper, get_username, get_mapset_ids

class RenBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('r!'), **kwargs)
        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print('Could not load extension {0} due to {1.__class__.__name__}: {1}'.format(cog, exc))

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))

APIHandler = APIWrapper(config.osu_token)
bot = RenBot()

# write general commands here

@bot.command(aliases=["v", "verif"])
async def verify(ctx, profile_url : str, *, user = None):
    if not user:
        user = ctx.author

    if not isinstance(user, discord.Member):
        ctx.send("Please send valid member as second argument!")
        return

    if not profile_url:
        await ctx.send("Please provide osu! profile link!")
        return
    
    osuUser = await APIWrapper(get_username(profile_url))
    if not osuUser:
        await ctx.send("Cannot find any user with that url, are you restricted?")
        return

    await ctx.send(f"Welcome, {osuUser.username}!")
    return

bot.run(config.token)
