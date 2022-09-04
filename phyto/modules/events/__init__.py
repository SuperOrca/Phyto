from phyto.core.bot import Phyto
from .events import Events


async def setup(bot: Phyto) -> None:
    await bot.add_cog(Events(bot))
