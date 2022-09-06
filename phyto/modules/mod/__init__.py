from phyto.core.bot import Phyto
from .mod import Moderation


async def setup(bot: Phyto) -> None:
    await bot.add_cog(Moderation(bot))
