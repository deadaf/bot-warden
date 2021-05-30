import discord
from datetime import datetime
from discord.ext import commands
from models import Bot
import humanize


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        if before.status == after.status:
            return

        if not before.bot or not before.id in self.bot.to_watch:
            return

        if after.status.value == "offline":
            await Bot.filter(bot_id=after.id).update(off_time=datetime.now())

        else:
            await Bot.filter(bot_id=after.id).update(start_time=datetime.now())

        self.bot.dispatch("log", after)

    @commands.Cog.listener()
    async def on_log(self, user):
        record = await Bot.get(bot_id=user.id)

        logschan = self.bot.get_channel(record.log_channel_id) or await self.bot.fetch_channel(record.log_channel_id)

        owner = self.bot.get_user(record.user_id) or await self.bot.fetch_user(record.user_id)

        content = getattr(owner, "mention", None)
        delta = (record.off_time - record.start_time).total_seconds()
        if user.status.value == "offline":
            embed = discord.Embed(color=discord.Color.red(), title=f"{str(user)} went Offline!")
            embed.description = f"Your bot {str(user)} [`{user.id}`] just went offline.\nIt was online for `{humanize.precisedelta(delta)}`"

        else:
            embed = discord.Embed(color=discord.Color.green(), title=f"{str(user)} has come online!")
            embed.description = f"Your bot {str(user)} [`{user.id}`] has come online.\nIt was offline for `{humanize.precisedelta(delta)}`"

        if logschan != None and logschan.permissions_for(logschan.guild).embed_links:
            await logschan.send(content=content, embed=embed)

        if record.dm:
            try:
                await owner.send(embed=embed)
            except:
                pass


def setup(bot):
    bot.add_cog(Events(bot))
