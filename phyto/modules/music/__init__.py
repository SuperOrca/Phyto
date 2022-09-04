from phyto.core.bot import Phyto
from .music import Music


async def setup(bot: Phyto) -> None:
    await bot.add_cog(Music(bot))
