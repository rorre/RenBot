#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
import sqlite3
from typing import Optional

import discord
from discord.ext import commands

import config
from helpers import db, embeds
from osuapi import APIWrapper, get_mapset_ids, get_username, make_api_kwargs

cogs = [
    'cogs.BotManagement',
    'cogs.RequestCommands',
    'cogs.UsersManager',
    'cogs.RoleManager'
]

class RenBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('r!'), **kwargs)
        for cog in cogs:
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
        ignored = (commands.CommandNotFound, commands.CheckFailure)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Missing required argument: " + error.param.name)
            
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr)
        return await ctx.send("An exception has occured: `{}`".format(error.__class__.__name__))

    async def on_member_join(self, member):
        print(f'[on_member_join] {member.name} joined.')
        await self.arrival_channel.send(f"Welcome, {member.mention}! Please verify yourself by sending `r!v <your osu! profile url`")

    async def on_member_remove(self, member):
        print(f'[on_member_join] {member.name} left.')
        await self.arrival_channel.send(f"Bye, {member.display_name}!")
        print(f'[on_member_join] Removing {member.name} from database.')
        await db.query([
            "DELETE FROM users WHERE uid = ?", [member.id]
        ])

bot = RenBot(owner_id=config.owner_id)
