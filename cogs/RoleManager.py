# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import config

class RoleManager(commands.Cog):
    """The description for Rolemanager goes here."""

    def __init__(self, bot):
        self.bot = bot
        self.allowed_roles = {
            'lewd' : '#nsfw access',
            'stream': 'live stream notification'
        }
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(config.guild_id)

        self.allowed_roles_id = {
        'lewd' : self.guild.get_role(638256184708694026),
        'stream' : self.guild.get_role(639078556902621184)
        }

    @commands.group()
    @commands.guild_only()
    async def role(self, ctx):
        pass
    
    @role.command()
    @commands.guild_only()
    async def get(self, ctx, role_name):
        if role_name not in self.allowed_roles:
            return await ctx.send("Invalid argument")
        await ctx.author.add_roles(self.allowed_roles_id[role_name])
        await ctx.send("Done!")

    @role.command()
    @commands.guild_only()
    async def remove(self, ctx, role_name):
        if role_name not in self.allowed_roles:
            return await ctx.send("Invalid argument")
        await ctx.author.remove_roles(self.allowed_roles_id[role_name])
        await ctx.send("Done!")



def setup(bot):
    bot.add_cog(RoleManager(bot))
