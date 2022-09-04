import logging
import sys
from os import listdir
from typing import List, Union

import aiohttp
import coloredlogs
import discord
import jishaku
import mystbin
from discord import Message
from discord.ext import commands

from .config import CONFIG
from .context import Context
from .logging import SetupLogging


class Phyto(commands.AutoShardedBot):
    @staticmethod
    async def _get_prefix(self, message: discord.Message) -> List[str]:
        return commands.when_mentioned_or(CONFIG["phyto"]["prefix"])(self, message)

    def __init__(self) -> None:
        super().__init__(
            command_prefix=self._get_prefix,
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions.none(),
            activity=discord.Activity(type=discord.ActivityType.watching, name="/help"),
            owner_ids=CONFIG["owner"]["ids"],
            strip_after_prefix=True,
            description=CONFIG["phyto"]["description"],
        )
        self.__version__ = CONFIG["phyto"]["version"]
        self.mentions = lambda message: (
            mention.strip() for mention in commands.when_mentioned(self, message)
        )
        coloredlogs.install()
        self.logger = logging.getLogger(__name__)

    async def get_context(self, message: discord.Message, *, cls=None) -> Context:
        return await super().get_context(message, cls=cls or Context)

    async def load(self) -> None:
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": f"Phyto v{self.__version__} ({CONFIG['phyto']['website']}) Python/{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__}"
            },
            timeout=aiohttp.ClientTimeout(total=30),
            loop=self.loop,
        )
        self.bin = mystbin.Client(session=self.session)

    async def load_modules(self) -> None:
        with SetupLogging(self.logger):
            for module in listdir("phyto/modules"):
                if "py" not in module:
                    await self.load_extension(f"phyto.modules.{module}")
            await self.load_extension("jishaku")
        jishaku.Flags.HIDE = True
        jishaku.Flags.NO_UNDERSCORE = True
        jishaku.Flags.NO_DM_TRACEBACK = True

    async def start(self) -> None:
        await super().start(CONFIG["phyto"]["token"], reconnect=True)

    async def setup_hook(self) -> None:
        self.logger.info("Running setup...")
        await self.load()

        self.logger.info(f"Database loaded")

        if not hasattr(self, "uptime"):
            self.uptime = discord.utils.utcnow()

        await self.load_modules()
        self.logger.info(f"Modules loaded ({len(self.extensions):,} loaded)")
        await super().setup_hook()

    async def on_ready(self) -> None:
        self.logger.info(
            f"Bot connected. DWSP latency:  {str(round((self.latency * 1000)))}ms"
        )

    async def on_message(self, message: discord.Message) -> Union[None, Message]:
        if message.author.bot or not message.guild:
            return
        if message.author.id in self.owner_ids and message.content.lower().startswith(
            "jsk"
        ):
            message.content = f"{self.user.mention} {message.content}"
        if message.content in self.mentions(message):
            return await message.reply(
                f"The server prefix is `{(await self._get_prefix(self, message))[-1]}`."
            )
        await self.process_commands(message)

    async def on_message_edit(
        self, before: discord.Message, after: discord.Message, /
    ) -> None:
        if after.author.id in self.owner_ids:
            if not before.embeds and after.embeds:
                return

            await self.process_commands(after)

    async def close(self) -> None:
        await self.session.close()
        await super().close()
