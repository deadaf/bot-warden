from discord.ext import commands
from tortoise import Tortoise
from datetime import datetime
import discord, asyncio
import config, cogs
from models import Bot
import contextlib
import logging
import aiohttp
import asyncpg
import os

os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"

# For basic bot logging
logger = logging.getLogger('WardenLog')
hdlr = logging.StreamHandler()
frmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', "%Y-%m-%d %H:%M:%S", style='{')
hdlr.setFormatter(frmt)
logger.addFilter(hdlr)

class RemoveNoise(logging.Filter):
    def __init__(self):
        super().__init__(name='discord.state')

    def filter(self, record):
        if record.levelname == 'WARNING' and 'referencing an unknown' in record.msg:
            return False
        return True

# For discord.py basic logging
@contextlib.contextmanager
def setup_logging():
    try:
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.state').addFilter(RemoveNoise())

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)

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
        logger.info('Hello World!')

        for ext in cogs.loadable:
            self.load_extension(ext)
            logger.info(f'Loaded Cog: {ext}')

    async def init_warden(self):
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.db = await asyncpg.create_pool(**config.POSTGRESQL)
        await Tortoise.init(config.TORTOISE)
        await Tortoise.generate_schemas(safe=True)
        await self.cache()

        # Initializing Models (Assigning Bot attribute to all models)
        for mname, model in Tortoise.apps.get("models").items():
            model.bot = self

        logger.info('Initialised Database Successfully!')

    async def cache(self):
        for idx in await Bot.filter(watch=True):
            self.to_watch.add(idx.bot_id)
        
        logger.info('Cache loaded!')

    async def on_ready(self):
        print(f"Logged in as: {self.user}")

    async def close(self) -> None:
        await super().close()
        await self.session.close()
        logger.info('Closing connections ....')

if __name__ == '__main__':
    bot = Warden()
    with setup_logging():
        bot.run(bot.config.DISCORD_TOKEN)
