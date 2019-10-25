# -*- coding: utf-8 -*-

from discord.ext import commands
from typing import Optional
import discord
import config
from osuapi import APIWrapper, get_username, get_mapset_ids, make_api_kwargs
from helpers import db, embeds
import asyncio

class OwnerCommands(commands.Cog):
    """The description for OwnerCommands goes here."""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.requests_channel = self.bot.get_channel(config.requests_channel)
        self.accepted_channel = self.bot.get_channel(config.accepted_channel)
        self.rejected_channel = self.bot.get_channel(config.rejected_channel)
        self.pending_channel = self.bot.get_channel(config.pending_channel)

    async def update_mid(self, req_id, mid : list):
        sql_query = """ UPDATE requests
                        SET message_id = ?
                        WHERE id = ?
                        """
        await db.query([
            sql_query,
            [
                ','.join(map(str, mid)), req_id
            ]
        ])

    @commands.command()
    @commands.is_owner()
    async def edit(self, ctx, request_id : int, is_accepted : bool, status : int, *, reason : str = ""):
        sql_res = await db.query([
            "SELECT * FROM requests WHERE id=?", [request_id]
        ])

        if not sql_res:
            await ctx.send("Cannot find that request.")
            return

        request = sql_res[0]

        request_mid = list(map(int, request[5].split(',')))
        messages = []
        messages.append(await self.requests_channel.fetch_message(request_mid[0]))

        channel_cases = {
            0: self.pending_channel,
            1: self.accepted_channel,
            2: self.accepted_channel,
            3: self.accepted_channel,
            4: self.rejected_channel
        }

        current_status = int(request[6])
        messages.append(await channel_cases[current_status].fetch_message(request_mid[1]))

        set_regex = get_mapset_ids(request[2])
        kwargs = make_api_kwargs(set_regex)

        status_embed = await embeds.generate_status_embed(status, reason=reason, **kwargs)
        
        await messages[0].edit(embed=status_embed)
        if channel_cases[current_status] != channel_cases[status]:
            await messages[1].delete()
        else:
            await messages[1].edit(embed=status_embed)

        sql_query = """ UPDATE requests
                        SET accepted = ?,
                            reason = ?,
                            status = ?
                        WHERE id = ?
                        """
        await db.query([
            sql_query,
            [
                is_accepted, reason, status, request_id
            ]
        ])

        return messages[0]

    @commands.command()
    @commands.is_owner()
    async def accept(self, ctx, request_id : int):
        msg = await self.edit.callback(self, ctx, request_id, 1, 1)
        accepted_msg = await self.accepted_channel.send(embed=msg.embeds[0])
        await self.update_mid(request_id, [msg.id, accepted_msg.id])

    @commands.command()
    @commands.is_owner()
    async def reject(self, ctx, request_id : int, *, reason : str):
        msg = await self.edit.callback(self, ctx, request_id, 0, 4, reason=reason)
        rejected_message = await self.rejected_channel.send(embed=msg.embeds[0])
        await self.update_mid(request_id, [msg.id, rejected_message.id])
    
    @commands.command()
    @commands.is_owner()
    async def edit_status(self, ctx, request_id : int, status : int):
        await self.edit.callback(self, ctx, request_id, 1, status)

def setup(bot):
    bot.add_cog(OwnerCommands(bot))
