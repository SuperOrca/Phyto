from typing import Optional

import discord
from discord.ext import commands
from mystbin import Paste

from .views import TrashView


class Context(commands.Context):
    async def reply(self, content: Optional[str] = None, **kwargs) -> discord.Message:
        if kwargs.pop("can_delete", False):
            view = TrashView(self)
            view.message = await super().reply(
                content, **kwargs, mention_author=False, view=view
            )
            return view.message

        else:
            return await super().reply(content, **kwargs, mention_author=False)

    async def send(self, content: Optional[str] = None, **kwargs) -> discord.Message:
        if kwargs.pop("can_delete", False):
            view = TrashView(self)
            view.message = await super().send(content, **kwargs, view=view)
            return view.message
        else:
            return await super().send(content, **kwargs)

    async def tick(self, tick: bool = True) -> None:
        try:
            if tick:
                await self.message.add_reaction("<:greenTick:596576670815879169>")
            elif tick is None:
                await self.message.add_reaction("<:grayTick:596576672900186113>")
            else:
                await self.message.add_reaction("<:redTick:596576672149667840>")
        except:
            ...

    async def paste(self, name: str, ext: str, content: str) -> Paste:
        return self.bot.bin.create_paste(
            filename=f"{name}.{ext}", syntax=ext, content=content
        )
