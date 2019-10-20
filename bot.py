#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import config

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


bot = RenBot()

# write general commands here

@bot.command(aliases=["v", "verif"])
async def verify(ctx, user : discord.Member, profile_url):
    if not user:
        await ctx.send("Please mention user!")
        return
    if not profile_url:
        await ctx.send("Please provide valid osu! profile link!")
        return
    

bot.run(config.token)
