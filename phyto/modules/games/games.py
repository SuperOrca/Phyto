from discord.ext import commands

from phyto.core.bot import Phyto


class Games(commands.Cog):
    def __init__(self, bot: Phyto) -> None:
        super().__init__()
        self.bot = bot
