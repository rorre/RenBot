# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
from helpers import db

import os

class BotManagement(commands.Cog):
    """Bot management stuffs."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def db(self, ctx, *, command):
        "Query database."
        if len(command) == 0:
            return await ctx.send("Needs a command.")
        cmd = command.strip("` ")
        sql_result = await db.query(cmd)
        return await ctx.send(str(sql_result))
    
    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        "Restart bot instance."
        await ctx.send("Restarting...")
        quit()
    
    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        "Pull updates from github and restart."
        await ctx.send("Updating bot...")
        os.system("git pull")
        quit()

def setup(bot):
    bot.add_cog(BotManagement(bot))
