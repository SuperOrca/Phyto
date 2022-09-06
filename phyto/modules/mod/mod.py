from discord.ext import commands

from phyto.core.bot import Phyto


class Moderation(commands.Cog):
    def __init__(self, bot: Phyto) -> None:
        super().__init__()
        self.bot = bot
