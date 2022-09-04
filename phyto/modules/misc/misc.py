import datetime
import sys
from typing import Optional

import discord
import humanize
from discord import ButtonStyle, ui
from discord.ext import commands

from phyto.core.bot import Phyto
from phyto.core.config import CONFIG
from phyto.core.context import Context
from phyto.core.embed import Embed
from phyto.core.exceptions import Error
from phyto.core.helpers import get_asset_url
from .help import HelpMenu


class Misc(commands.Cog):
    def __init__(self, bot: Phyto) -> None:
        super().__init__()
        self.bot = bot
        self.icon = "⚙"

        bot.help_command = None
        self.map = {}

    @commands.hybrid_command(
        "bot",
        description="⚙ Information about the bot",
        aliases=["uptime", "about", "source", "invite"],
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _bot(self, ctx: Context) -> None:
        icon = get_asset_url(self.bot.user.avatar)
        version_info = sys.version_info

        data = await (
            await self.bot.session.get(
                "https://api.github.com/repos/SuperOrca/phyto/commits"
            )
        ).json()
        changes = ""

        for commit in data[:3]:
            time = datetime.datetime.strptime(
                commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=datetime.timezone.utc)
            changes += f"[`{commit['sha'][:6]}`]({commit['html_url']}) {commit['commit']['message']} ({discord.utils.format_dt(time, 'R')})\n "

        await ctx.reply(
            embed=Embed.default(
                description=f"""
{CONFIG['phyto']['description']}

➤ ID: `{self.bot.user.id}`
➤ Created: {discord.utils.format_dt(self.bot.user.created_at, "R")}
➤ Owner: [`{CONFIG['owner']['name']}`]({CONFIG['owner']['website']})
➤ Uptime: `{humanize.precisedelta(discord.utils.utcnow() - self.bot.uptime)}`
➤ Python: `v{version_info[0]}.{version_info[1]}.{version_info[2]}`
➤ Library: `discord.py` (`v{discord.__version__}`)
            """,
            )
            .set_author(
                name=f"{self.bot.user} | v{self.bot.__version__}",
                icon_url=icon,
            )
            .add_field(name="Latest Changes", value=changes)
            .add_field(
                name="Statistics",
                value=f"""
➤ Commands: `{len(list(filter(lambda cmd: cmd.description, self.bot.commands))):,}`
➤ Servers: `{len(self.bot.guilds):,}`
➤ Users: `{len(self.bot.users):,}`
                """,
                inline=False,
            )
            .set_thumbnail(url=icon),
            view=ui.View().add_item(
                ui.Button(
                    style=ButtonStyle.link,
                    label="Website",
                    url=CONFIG["phyto"]["website"],
                )
            ),
        )

    @commands.hybrid_command("ping", description="⚙ Pings the bot")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _ping(self, ctx: Context) -> None:
        await ctx.reply(
            embed=Embed.default(
                description=f"Pong! `{round(self.bot.latency * 1000)}ms`"
            )
        )

    @commands.hybrid_command(
        "help", description="⚙ Shows the help menu", help="[command]"
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _help(self, ctx: Context, command: Optional[str] = None) -> None:
        if command:
            if not self.map:
                for cmd in self.bot.walk_commands():
                    if cmd.description:
                        self.map[cmd.name] = cmd
                        for aliase in cmd.aliases:
                            self.map[aliase] = cmd
            command = command.lower()
            if command in self.map:
                command = self.map[command]
                aliases = (
                    ", ".join(f"`{aliase}`" for aliase in command.aliases)
                    if len(command.aliases) > 0
                    else "`No aliases.`"
                )
                parts = command.description.split(" ")
                module = command.cog.__cog_name__
                icon = parts[0]
                description = " ".join(parts[1:])
                cooldown = command.cooldown.rate

                await ctx.reply(
                    embed=Embed.default(
                        title=f"`{ctx.clean_prefix}{command.name}` {command.help or ''}",
                        description=f"""
{description}

➤ Module: {icon} `{module}`           
➤ Aliases: {aliases}
➤ Cooldown: `{cooldown} seconds`
""",
                    )
                )
            else:
                raise Error(f"Command `{command}` not found.")
        else:
            await HelpMenu(
                ctx,
            ).start()
