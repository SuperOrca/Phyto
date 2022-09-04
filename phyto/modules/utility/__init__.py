from phyto.core.bot import Phyto
from .utility import Utility


async def setup(bot: Phyto) -> None:
    await bot.add_cog(Utility(bot))
