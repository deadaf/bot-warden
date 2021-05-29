from discord.ext import commands
from tortoise import Tortoise
from datetime import datetime
import discord, asyncio
import config, cogs
from models import Bot
import aiohttp
import asyncpg
import os


os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"


class Warden(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=("w.", "W."),
            strip_after_prefix=True,
            case_insensitive=True,
            intents=discord.Intents.all(),
            chunk_guilds_at_startup=False,
            **kwargs,
        )

        self.config = config
        self.color = config.COLOR
        self.start_time = datetime.now()
        self.loop = asyncio.get_event_loop()
        self.to_watch = set()
        asyncio.get_event_loop().run_until_complete(self.init_warden())

        for ext in cogs.loadable:
            self.load_extension(ext)

    async def init_warden(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.db = await asyncpg.create_pool(**config.POSTGRESQL)
        await Tortoise.init(config.TORTOISE)
        await Tortoise.generate_schemas(safe=True)
        await self.cache()

        # Initializing Models (Assigning Bot attribute to all models)
        for mname, model in Tortoise.apps.get("models").items():
            model.bot = self

    async def cache(self):
        for idx in await Bot.filter(watch=True):
            self.to_watch.add(idx.bot_id)

    async def on_ready(self):
        print(f"Logged in as: {self.user}")

    async def close(self) -> None:
        await super().close()
        await self.session.close()


bot = Warden()
bot.run(bot.config.DISCORD_TOKEN)
