#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
from typing import Optional
import discord
import config
from osuapi import APIWrapper, get_username, get_mapset_ids
from helpers import db

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
    
    osuUser = await APIHandler.get_users(get_username(profile_url))
    if not osuUser:
        await ctx.send("Cannot find any user with that url, are you restricted?")
        return

    osuUser = osuUser[0]
    guild_roles = ctx.guild.roles
    verified_role = list(filter(lambda x: x.name == " Verified", guild_roles))[0]
    await ctx.send(f"Welcome, {osuUser.username}!")
    await user.add_roles(verified_role)

@bot.command(aliases=["r", "req"])
async def request(ctx, map_url : str):
    previous_requests = await db.query(
        ["SELECT * FROM requests WHERE requester_uid=?", [ctx.author.id]]
    )
    
    if previous_requests:
        ongoing_reqs = list(filter(lambda x: not x[3], previous_requests))
        if ongoing_reqs:
            await ctx.send("You have sent another request before: " + ongoing_reqs[0][2])
            return
    
    hmm = await db.query(
        ["INSERT INTO requests (requester_uid, mapset_url) VALUES (?,?)",
        [ctx.author.id, map_url]]
    )
    print(hmm)
    await ctx.send("Sent!")

bot.run(config.token)
