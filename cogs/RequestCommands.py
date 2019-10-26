# -*- coding: utf-8 -*-

import asyncio
from typing import Optional

import discord
from discord.ext import commands

import config
from helpers import db, embeds
from osuapi import APIWrapper, get_mapset_ids, get_username, make_api_kwargs


class OwnerCommands(commands.Cog):
    """Owner only commands."""
    qualified_name = "Owner"

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.requests_channel = self.bot.get_channel(config.requests_channel)
        self.accepted_channel = self.bot.get_channel(config.accepted_channel)
        self.rejected_channel = self.bot.get_channel(config.rejected_channel)
        self.pending_channel = self.bot.get_channel(config.pending_channel)

    async def update_mid(self, req_id, mid: list):
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
    @commands.guild_only()
    async def edit(self, ctx, request_id: int, is_accepted: bool, status: int, *, reason: str = ""):
        """Edits request object.
        
        - First parameter should be is_accepted's value, could be 0 or 1.
        - Second parameter should be an integer
        - Status are considered with these maps:
            1: Accepted
            2: Modding
            3: Done
            4: Rejected
        - If status is 4, then reasoning should be provided."""
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
    @commands.guild_only()
    async def accept(self, ctx, request_id: int):
        "Accepts a request. | Owner only"
        msg = await self.edit.callback(self, ctx, request_id, 1, 1)
        accepted_msg = await self.accepted_channel.send(embed=msg.embeds[0])
        await self.update_mid(request_id, [msg.id, accepted_msg.id])

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def reject(self, ctx, request_id: int, *, reason: str):
        "Rejects a request. | Owner only"
        msg = await self.edit.callback(self, ctx, request_id, 0, 4, reason=reason)
        rejected_message = await self.rejected_channel.send(embed=msg.embeds[0])
        await self.update_mid(request_id, [msg.id, rejected_message.id])

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def edit_status(self, ctx, request_id: int, status: int):
        "Edits request status. | Owner only"
        await self.edit.callback(self, ctx, request_id, 1, status)

    @commands.command(aliases=["r", "req"])
    @commands.guild_only()
    async def request(self, ctx, map_url: str):
        """Requests a mod
        
        - If the user already have ongoing request, it will be rejected."""
        print(f"[request] Querying database to see if {ctx.author.name} has ongoing request")
        previous_requests = await db.query(
            ["SELECT * FROM requests WHERE requester_uid=?", [ctx.author.id]]
        )

        is_owner = await self.bot.is_owner(ctx.author)

        if previous_requests and not is_owner:
            ongoing_reqs = list(filter(lambda x: int(
                x[6]) not in [3, 4], previous_requests))
            if ongoing_reqs:
                await ctx.send("You have sent another request before: " + ongoing_reqs[0][2])
                return

        print(f"[request] Getting osu!map url")
        set_regex = get_mapset_ids(map_url)

        if not set_regex:
            await ctx.send("Please send valid beatmap!")
            return

        kwargs = make_api_kwargs(set_regex)

        print("[request] Generating embed")
        request_embed = await embeds.generate_request_embed(**kwargs)

        if not request_embed:
            await ctx.send("Cannot find mapset from osu! API")
            return

        print("[request] Posting embeds")
        request_messages = [
            await self.bot.requests_channel.send(embed=request_embed),
            await self.bot.pending_channel.send(embed=request_embed)
        ]

        print("[request] Querying database for map")
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



def setup(bot):
    bot.add_cog(OwnerCommands(bot))
