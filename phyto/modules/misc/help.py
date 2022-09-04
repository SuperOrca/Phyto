import discord
from discord import ui
from discord.utils import MISSING

from phyto.core.context import Context
from phyto.core.embed import Embed
from phyto.core.helpers import chunks


class HelpSelect(ui.Select):
    def __init__(self, ctx: Context, view: ui.View):
        options = [
            discord.SelectOption(label="Phyto", emoji="<:phyto:1016014049974169671>")
        ]
        for cog in ctx.bot.cogs.values():
            if hasattr(cog, "icon"):
                options.append(
                    discord.SelectOption(label=cog.__cog_name__, emoji=cog.icon)
                )
        super().__init__(options=options)

    async def callback(self, interaction: discord.Interaction):
        self.options[0].default = False
        await self.view.to_page(interaction, self.values[0])


class HelpMenu(ui.View):
    def __init__(self, ctx: Context) -> None:
        super().__init__(timeout=300)
        self.page_embeds = None
        self.page = None
        self.message = None
        self.ctx = ctx
        self.bot = ctx.bot
        self.index = 0
        self.setup_options()
        self.add_item(HelpSelect(ctx, self))
        self.update()

    def setup_options(self):
        self.page = "Phyto"
        self.page_embeds = {
            "Phyto": [
                Embed.default(
                    title="<:phyto:1016014049974169671> Phyto Help",
                    description=f"""
➤ Use `{self.ctx.clean_prefix}help <command>` for more information about a command.
➤ For more information about the bot use `{self.ctx.clean_prefix}bot`.

➤ Select a module to view the commands it contains.
""",
                )
            ]
        }
        options = [
            discord.SelectOption(
                label="Phyto", emoji="<:phyto:1016014049974169671>", default=True
            )
        ]
        for cog in self.bot.cogs.values():
            if hasattr(cog, "icon"):
                options.append(
                    discord.SelectOption(label=cog.__cog_name__, emoji=cog.icon)
                )
                self.page_embeds[cog.__cog_name__] = []
                for chunk in chunks(cog.get_commands(), 5):
                    description = f"➤ Use `{self.ctx.clean_prefix}help <command>` for more information about a command.\n\n"
                    for command in chunk:
                        description += f"`{self.ctx.clean_prefix}{command}` {' '.join(command.description.split(' ')[1:])}\n"
                    self.page_embeds[cog.__cog_name__].append(
                        Embed.default(
                            title=f"{cog.icon} {cog.__cog_name__}",
                            description=description,
                        )
                    )

    async def to_page(self, interaction: discord.Interaction, page: str):
        self.page = page
        await self.show_page(interaction, 0)

    @property
    def embeds(self):
        return self.page_embeds[self.page]

    @property
    def max_index(self):
        return len(self.embeds) - 1

    @property
    def human_index(self):
        return self.index + 1

    @property
    def human_max_index(self):
        return len(self.embeds)

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
        self.message = await self.ctx.reply(embed=self.embeds[0], view=self)

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
