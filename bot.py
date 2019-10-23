#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
from typing import Optional
import discord
import config
from osuapi import APIWrapper, get_username, get_mapset_ids
from helpers import db, embeds

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
        self.requests_channel = self.get_channel(config.requests_channel)

APIHandler = APIWrapper(config.osu_token)
bot = RenBot(owner_id=config.owner_id)

def make_api_kwargs(regex_res):
    kwargs = {}
    if regex_res[0] in ['s', 'beatmapsets']:
        kwargs['s'] = regex_res[1]
    else:
        kwargs['b'] = regex_res[1]
    return kwargs

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
    
    is_owner = await bot.is_owner(ctx.author)

    if previous_requests and not is_owner:
        ongoing_reqs = list(filter(lambda x: int(x[6]) not in [3,4], previous_requests))
        if ongoing_reqs:
            await ctx.send("You have sent another request before: " + ongoing_reqs[0][2])
            return

    set_regex = get_mapset_ids(map_url)
    kwargs = make_api_kwargs(set_regex)

    request_embed = await embeds.generate_request_embed(**kwargs)
    request_message = await bot.requests_channel.send(embed=request_embed)
    await db.query(
        ["INSERT INTO requests (requester_uid, mapset_url, message_id) VALUES (?,?,?)",
        [ctx.author.id, map_url, request_message.id]]
    )
    dbid = await db.query("SELECT id FROM requests ORDER BY id DESC LIMIT 1;") # really inefficient aaaaa
    await request_message.edit(content=f"ID: **{dbid[0][0]}**")
    await ctx.send("Sent!")

@bot.command()
@commands.is_owner()
async def edit(ctx, request_id : int, is_accepted : bool, status : int, *, reason : str = ""):
    sql_res = await db.query([
        "SELECT * FROM requests WHERE id=?", [request_id]
    ])
    request = sql_res[0]
    message = await ctx.fetch_message(int(request[5]))

    set_regex = get_mapset_ids(request[2])
    kwargs = make_api_kwargs(set_regex)

    status_embed = await embeds.generate_status_embed(status, reason=reason, **kwargs)
    await message.edit(embed=status_embed)

    sql_query = """ UPDATE requests
                    SET accepted = ?,
                        reason = ?,
                        status = ?
                    WHERE id = ?
                    """
    await db.query([sql_query, [is_accepted, reason, status, request_id]])

bot.run(config.token)
