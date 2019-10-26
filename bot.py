#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
from typing import Optional

import discord
from discord.ext import commands

import config
from helpers import db, embeds
from osuapi import APIWrapper, get_mapset_ids, get_username, make_api_kwargs


class RenBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('r!'), **kwargs)
        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print('Could not load extension {0} due to {1.__class__.__name__}: {1}'.format(
                    cog, exc))

    async def on_ready(self):
        print('Logged on as {0} (ID: {0.id})'.format(self.user))
        self.requests_channel = self.get_channel(config.requests_channel)
        self.pending_channel = self.get_channel(config.pending_channel)
        self.arrival_channel = self.get_channel(config.arrival_channel)

    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Missing required argument: " + error.param.name)
            
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)
        return await ctx.send("An exception has occured: `{}`".format(error.__class__.__name__))

    async def on_member_join(self, member):
        await self.arrival_channel.send(f"Welcome, {member.mention}! Please verify yourself by sending `r!v <your osu! profile url`")

APIHandler = APIWrapper(config.osu_token)
bot = RenBot(owner_id=config.owner_id)

# write general commands here


@bot.command(aliases=["v", "verif"])
async def verify(ctx, profile_url: str, *, user=None):
    """Verifies a user
    
    - The only parameter is profile url.
    - There is one optional parameter, it is target user."""
    if not user:
        user = ctx.author

    if not isinstance(user, discord.Member):
        ctx.send("Please send valid member as second argument!")
        return

    if not profile_url:
        await ctx.send("Please provide osu! profile link!")
        return

    username = get_username(profile_url)
    if not username:
        await ctx.send("Um... I cannot find username/id from your url, are you sure its correct?")
        return

    osuUser = await APIHandler.get_users(username)
    if not osuUser:
        await ctx.send("Cannot find any user with that url, are you restricted?")
        return

    osuUser = osuUser[0]
    guild_roles = ctx.guild.roles
    verified_role = list(filter(lambda x: x.name.lower() == "verified", guild_roles))
    if not verified_role:
        await ctx.send("Cannot find Verified role, ping admin please.")
        return
    verified_role = verified_role[0]
    await ctx.send(f"Welcome, {osuUser.username}!")
    await user.add_roles(verified_role)


@bot.command(aliases=["r", "req"])
async def request(ctx, map_url: str):
    """Requests a mod
    
    - If the user already have ongoing request, it will be rejected."""
    previous_requests = await db.query(
        ["SELECT * FROM requests WHERE requester_uid=?", [ctx.author.id]]
    )

    is_owner = await bot.is_owner(ctx.author)

    if previous_requests and not is_owner:
        ongoing_reqs = list(filter(lambda x: int(
            x[6]) not in [3, 4], previous_requests))
        if ongoing_reqs:
            await ctx.send("You have sent another request before: " + ongoing_reqs[0][2])
            return

    set_regex = get_mapset_ids(map_url)

    if not set_regex:
        await ctx.send("Please send valid beatmap!")
        return

    kwargs = make_api_kwargs(set_regex)

    request_embed = await embeds.generate_request_embed(**kwargs)

    if not request_embed:
        await ctx.send("Cannot find mapset from osu! API")
        return

    request_messages = [
        await bot.requests_channel.send(embed=request_embed),
        await bot.pending_channel.send(embed=request_embed)
    ]

    await db.query([
        "INSERT INTO requests (requester_uid, mapset_url, message_id, status) VALUES (?,?,?,?)",
        [
            ctx.author.id,
            map_url,
            ','.join(map(lambda x: str(x.id), request_messages)),
            0
        ]
    ])

    # really inefficient aaaaa
    dbid = await db.query("SELECT id FROM requests ORDER BY id DESC LIMIT 1;")
    await request_messages[0].edit(content=f"ID: **{dbid[0][0]}**")

    await ctx.send("Sent!")
