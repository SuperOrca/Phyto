from phyto.core.bot import Phyto
from .fun import Fun


async def setup(bot: Phyto) -> None:
    await bot.add_cog(Fun(bot))
