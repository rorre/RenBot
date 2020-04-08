# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import config

class RoleManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.roles = config.roles
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(config.guild_id)

    @commands.group()
    @commands.guild_only()
    async def role(self, ctx):
        if not ctx.invoked_subcommand:
            return await ctx.send("Please invoke a subcommand.")
    
    @role.command()
    @commands.guild_only()
    async def get(self, ctx, role_name):
        if role_name not in self.roles:
            return await ctx.send("Invalid argument")
        role = self.guild.get_role(self.roles[role_name][1])
        if role in self.ctx.author.roles:
            return await ctx.send("You already have that role.")
        await ctx.author.add_roles(role)
        await ctx.send("Done!")

    @role.command()
    @commands.guild_only()
    async def remove(self, ctx, role_name):
        if role_name not in self.roles:
            return await ctx.send("Invalid argument")
        role = self.guild.get_role(self.roles[role_name][1])
        if role not in self.ctx.author.roles:
            return await ctx.send("You don't have that role.")
        await ctx.author.remove_roles(role)
        await ctx.send("Done!")

    @role.command()
    @commands.guild_only()
    async def info(self, ctx, *, role_name):
        if role_name not in self.roles:
            return await ctx.send("Invalid argument")
        role_desc = self.roles[role_name][0]
        await ctx.send(f"`{role_name}`: `{role_desc}`")


def setup(bot):
    bot.add_cog(RoleManager(bot))
