# -*- coding: utf-8 -*-

import sys
import traceback
import sqlite3
import asyncio
from typing import Optional

import discord
from discord.ext import commands, tasks

import config
from helpers import db, embeds
from osuapi import APIWrapper, get_mapset_ids, get_username, make_api_kwargs

APIHandler = APIWrapper(config.osu_token)

def check_channel(ctx):
    return ctx.message.channel.id == config.arrival_channel

class UsersManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.username_checker.start()
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(config.guild_id)
    
    def cog_unload(self):
        self.username_checker.cancel()

    @tasks.loop(hours=2)
    async def username_checker(self):
        print("[username_checker] START")
        print("[username_checker] querying database")
        users = await db.query("SELECT * FROM users")
        for u in users:
            print("[username_checker] Gathering user:", u[0])
            member = await self.guild.fetch_member(u[0])
            print("[username_checker] Gathering osu! profile for:", member.name)
            osuUser = await APIHandler.get_users(u[1])
            if not osuUser:
                continue
            osuUser = osuUser[0]
            print("[username_checker] Renaming to:", osuUser.username)
            await member.edit(nick=osuUser.username)
            await asyncio.sleep(10)
    
    @username_checker.before_loop
    async def before_checks(self):
        print('[username_checker] Waiting for bot to be ready')
        await self.bot.wait_until_ready()

    @commands.command(aliases=["v", "verif"])
    @commands.guild_only()
    @commands.check(check_channel)
    async def verify(self, ctx, profile_url: str, *, user=None):
        """Verifies a user
        
        - The only parameter is profile url.
        - There is one optional parameter, it is target user."""
        if not user:
            user = ctx.author
        else:
            if not await self.bot.is_owner(ctx.author):
                return ctx.send("Only owner could do that.")

        if not isinstance(user, discord.Member):
            await ctx.send("Please send valid member as second argument!")
            return

        if not profile_url:
            await ctx.send("Please provide osu! profile link!")
            return

        print("[verify] Getting username from url")
        username = get_username(profile_url)
        if not username:
            await ctx.send("Um... I cannot find username/id from your url, are you sure its correct?")
            return

        print("[verify] Getting user from osu! API")
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

        print(f"[verify] Inputting user {osuUser.user_id} to database")
        try:
            await db.query([
                "INSERT into users (uid, osu_uid) VALUES(?,?);",
                [user.id, osuUser.user_id]
            ])
        except sqlite3.IntegrityError:
            await ctx.send("Somebody else have used that username. (or you're already verified)")
            return
        
        verified_role = verified_role[0]
        await ctx.send(f"Welcome, {osuUser.username}!")
        await user.add_roles(verified_role)
        await user.edit(nick=osuUser.username)


def setup(bot):
    bot.add_cog(UsersManager(bot))
