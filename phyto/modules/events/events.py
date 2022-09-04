import math

from discord.ext import commands

from phyto.core.bot import Phyto
from phyto.core.context import Context
from phyto.core.embed import Embed
from phyto.core.exceptions import Error


class Events(commands.Cog):
    def __init__(self, bot: Phyto) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, Error):
            await ctx.reply(
                embed=Embed.error(description=error),
                can_delete=True,
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                embed=Embed.error(
                    description=f"You are missing the required `{error.param.name}` argument."
                ),
                can_delete=True,
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                embed=Embed.error(
                    description=f"You are on cooldown for `{math.ceil(error.retry_after * 10) / 10}s`."
                ),
                can_delete=True,
            )
        else:
            await ctx.reply(
                embed=Embed.error(
                    description="An unknown error has occured. The developers have been alerted."
                ),
                can_delete=True,
            )

            self.bot.logger.error(error)
