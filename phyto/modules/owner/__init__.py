from phyto.core.bot import Phyto
from .owner import Owner


async def setup(bot: Phyto) -> None:
    await bot.add_cog(Owner(bot))
