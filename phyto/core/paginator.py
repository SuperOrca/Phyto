import discord
from discord import ui
from discord.utils import MISSING

from .context import Context
from .embed import Embed
from .types import Iterable


class EmbedPaginatorMenu(ui.View):
    def __init__(self, ctx: Context, embeds: Iterable[Embed]) -> None:
        super().__init__(timeout=300)
        self.message = None
        self.ctx = ctx
        self.embeds = embeds
        self.index = 0
        self.max_index = len(embeds) - 1
        self.update()

    @property
    def human_index(self):
        return self.index + 1

    @property
    def human_max_index(self):
        return self.max_index + 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.ctx.author != interaction.user:
            await interaction.response.send_message(
                embed=Embed.error(
                    description=f"This view is owned by {self.ctx.author.mention}. You make your own view by using the `{self.ctx.command}` command."
                ),
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        self.clear_items()
        await self.message.edit(view=self)

    async def start(self):
        self.message = await self.ctx.send(embed=self.embeds[0], view=self)

    async def show_page(self, interaction: discord.Interaction, index: int):
        self.index = index
        self.update()
        await interaction.response.edit_message(
            embed=self.embeds[self.index], view=self
        )

    def update(self):
        self.beginning.disabled = self.index <= 0
        self.back.disabled = self.index <= 0
        self.next.disabled = self.index >= self.max_index
        self.end.disabled = self.index >= self.max_index
        self.seperator.label = f"{self.human_index}/{self.human_max_index}"

    @ui.button(emoji="⏪", style=discord.ButtonStyle.secondary)
    async def beginning(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        await self.show_page(interaction, 0)

    @ui.button(emoji="⬅", style=discord.ButtonStyle.secondary)
    async def back(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        await self.show_page(interaction, self.index - 1)

    @ui.button(label=MISSING, style=discord.ButtonStyle.primary, disabled=True)
    async def seperator(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        ...

    @ui.button(emoji="➡", style=discord.ButtonStyle.secondary)
    async def next(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        await self.show_page(interaction, self.index + 1)

    @ui.button(emoji="⏩", style=discord.ButtonStyle.secondary)
    async def end(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        await self.show_page(interaction, self.max_index)
