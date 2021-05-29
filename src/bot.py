from discord.ext import commands
from tortoise import Tortoise
from datetime import datetime
import discord, asyncio
import config, cogs
import aiohttp
import asyncpg

intents = discord.Intents.default()
intents.presences = True


class Warden(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=("w.", "W."),
            strip_after_prefix=True,
            case_insensitive=True,
            intents=intents,
            **kwargs,
        )

        self.config = config
        self.color = config.COLOR
        self.start_time = datetime.now()
        self.loop = asyncio.get_event_loop()
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
        pass

    async def on_ready(self):
        print(f"Logged in as: {self.user}")

    async def close(self) -> None:
        await super().close()
        await self.session.close()


bot = Warden()
bot.run(bot.config.DISCORD_TOKEN)
