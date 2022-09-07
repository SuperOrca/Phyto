import math

from discord.ext import commands

from phyto.core.bot import Phyto
from phyto.core.context import Context
from phyto.core.embed import Embed
from phyto.core.exceptions import Error
from phyto.core.views import TrashView


class Events(commands.Cog):
    def __init__(self, bot: Phyto) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, Error):
            await ctx.send(
                embed=Embed.error(description=error),
                view=TrashView(ctx),
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=Embed.error(
                    description=f"You are missing the required `{error.param.name}` argument."
                ),
                view=TrashView(ctx),
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                embed=Embed.error(
                    description=f"You are on cooldown for `{math.ceil(error.retry_after * 10) / 10}s`."
                ),
                view=TrashView(ctx),
            )
        else:
            await ctx.send(
                embed=Embed.error(
                    description="An unknown error has occured. The developers have been alerted."
                ),
                view=TrashView(ctx),
            )

            self.bot.logger.error(error)
