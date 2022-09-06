from discord.ext import commands
from mystbin import Paste


class Context(commands.Context):
    async def paste(self, name: str, ext: str, content: str) -> Paste:
        return self.bot.bin.create_paste(
            filename=f"{name}.{ext}", syntax=ext, content=content
        )
