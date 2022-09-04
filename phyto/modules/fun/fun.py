import datetime

import discord.utils
from discord.ext import commands

from phyto.core.bot import Phyto
from phyto.core.context import Context
from phyto.core.embed import Embed


class Fun(commands.Cog):
    def __init__(self, bot: Phyto) -> None:
        super().__init__()
        self.bot = bot
        self.icon = "🙂"
        self.christmas_day = datetime.datetime(2022, 12, 25)

    @commands.hybrid_command("christmas", description="🙂 Amount of days till Christmas")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _christmas(self, ctx: Context) -> None:
        await ctx.reply(
            embed=Embed.default(
                description=f"Christmas is {discord.utils.format_dt(self.christmas_day, 'R')}."
            )
        )
