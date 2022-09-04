from phyto.core.bot import Phyto
from .misc import Misc


async def setup(bot: Phyto) -> None:
    await bot.add_cog(Misc(bot))
