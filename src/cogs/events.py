import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.status == after.status:
            return

        if before.id not in self.bot.to_watch:
            return


def setup(bot):
    bot.add_cog(Events(bot))
