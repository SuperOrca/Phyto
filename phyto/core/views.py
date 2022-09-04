import discord
from discord import ui
from discord.ext import commands

from .embed import Embed


class TrashView(ui.View):
    def __init__(self, ctx: commands.Context) -> None:
        super().__init__(timeout=300)
        self.message = None
        self.ctx = ctx

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

    @ui.button(emoji="🗑️", style=discord.ButtonStyle.secondary)
    async def delete(
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        await interaction.message.delete()
        self.stop()
