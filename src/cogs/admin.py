import discord
from models import Bot
from discord.ext import commands
from datetime import datetime
from typing import Optional


class WatchID(commands.Converter):
    async def convert(self, ctx, argument) -> Optional[Bot]:
        if not argument.isdigit():
            raise commands.BadArgument(f"This is not a valid watch ID.\n\nGet a valid ID with `{ctx.prefix}all`")

        record = await Bot.get_or_none(id=int(argument), user_id=ctx.author.id)
        if not record:
            raise commands.BadArgument(f"This is not a valid watch ID.\n\nGet a valid ID with `{ctx.prefix}all`")

        return record


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup(self, ctx, bot: discord.Member, channel: discord.TextChannel):
        records = await Bot.filter(user_id=ctx.author.id).count()

        if records == 4:
            return await ctx.send(f"You can't setup more than 4 bots.")

        if not channel.permissions_for(ctx.me).embed_links:
            return await ctx.send(f"I need embed_links , send_messages permission in {channel.mention}")

        if not bot.bot:  # bot.bot lol
            return await ctx.send(f"{str(bot)} is not a bot.")

        check = await Bot.filter(bot_id=bot.id, user_id=ctx.author.id)
        if len(check):
            return await ctx.send(f"You cannot setup a bot twice.")

        if bot.status.value == "offline":
            start_time = None
            off_time = datetime.now()
        else:
            start_time = datetime.now()
            off_time = None

        record = await Bot.create(
            bot_id=bot.id,
            user_id=ctx.author.id,
            guild_id=ctx.guild.id,
            log_channel_id=channel.id,
            start_time=start_time,
            off_time=off_time,
        )
        self.bot.to_watch.add(bot.id)
        await ctx.send(
            f"Alright! I will watch over {bot.mention} for you.\nWatch Id for the bot is `{record.id}`, you will need it later."
        )

    @commands.command()
    async def dm(self, ctx, watch_id: WatchID):
        await Bot.filter(id=watch_id.id).update(dm=not (watch_id.dm))
        await ctx.send(f"DM notficattions for `{watch_id.id}` turned {'ON' if not watch_id.dm else 'OFF'}!")

    @commands.command()
    async def all(self, ctx):
        records = await Bot.filter(user_id=ctx.author.id)
        if not len(records):
            return await ctx.send(f"You haven't setup any bot yet.")

        mystr = ""
        for idx, record in enumerate(records, start=1):
            bot = self.bot.get_user(record.bot_id) or await self.bot.fetch_user(record.bot_id)
            mystr += f"{idx:02}. **{bot}** (Watch ID: {record.id})"
        await ctx.send(mystr)

    @commands.command()
    async def delete(self, ctx, watch_id: WatchID):
        await Bot.filter(id=watch_id.id).delete()
        self.bot.to_watch.discard(watch_id.id)
        await ctx.send(f"Stopped watch for {watch_id.id}")


def setup(bot):
    bot.add_cog(Admin(bot))
