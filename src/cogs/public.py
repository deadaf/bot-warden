import discord
from discord.ext import commands


class Public(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        await ctx.send(f"<{self.bot.config.INVITE}>")

    @commands.command()
    async def support(self, ctx):
        await ctx.send(self.bot.config.SERVER)

    @commands.command()
    async def stats(self, ctx):
        text = f"{len(self.bot.guilds)} Servers\n{sum(g.member_count for g in self.bot.guilds)} Members"
        await ctx.send(text)


def setup(bot):
    bot.add_cog(Public(bot))
