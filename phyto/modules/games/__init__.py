from phyto.core.bot import Phyto
from .games import Games


async def setup(bot: Phyto) -> None:
    await bot.add_cog(Games(bot))
