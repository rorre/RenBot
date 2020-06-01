# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import re

pattern = re.compile("(\d+:\d+:\d+ [(|,1-9) ]*-)")

class OsuHelper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        content = message.content
        if self.bot.user == author:
            return
        
        timestamps = pattern.findall(content)
        if not timestamps:
            return
        
        timestamps = list(set(timestamps))
        for ts in timestamps:
            ts_url = f"<osu://edit/{ts[:-2].replace(' ', '_')}> -"
            content = content.replace(ts, ts_url)
        
        embed = discord.Embed(
            title="",
            colour=discord.Colour(0x4a90e2),
            description=content
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar_url)
        await message.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(OsuHelper(bot))
