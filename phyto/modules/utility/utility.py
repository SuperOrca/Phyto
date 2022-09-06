import random
from io import BytesIO
from typing import Optional

import discord
from PIL import Image
from discord import UserFlags, ui, ButtonStyle, app_commands
from discord.ext import commands

from phyto.core.bot import Phyto
from phyto.core.color import Color
from phyto.core.context import Context
from phyto.core.embed import Embed
from phyto.core.exceptions import Error
from phyto.core.helpers import get_asset_url, get_permissions


class Utility(commands.Cog):
    def __init__(self, bot: Phyto) -> None:
        super().__init__()
        self.bot = bot
        self.icon = "⚒"

        self.flags = {
            UserFlags.staff: 1010398943600984135,
            UserFlags.partner: 1010398947690430565,
            UserFlags.hypesquad: 1010398944704069642,
            UserFlags.bug_hunter: 1010409895423651891,
            UserFlags.hypesquad_bravery: 1010398940069376021,
            UserFlags.hypesquad_brilliance: 1010398941017280594,
            UserFlags.hypesquad_balance: 1010398939071127663,
            UserFlags.early_supporter: 1010398942405607466,
            UserFlags.bug_hunter_level_2: 1010398941902282762,
            UserFlags.verified_bot: 1010398938244845668,
            UserFlags.verified_bot_developer: 1010411414474719282,
            UserFlags.discord_certified_moderator: 1010191673906700399,
        }

    def get_flags(self, member: discord.Member) -> str:
        all = member.public_flags.all()
        if len(all) < 1:
            return "`No flags.`"
        return " ".join(str(self.bot.get_emoji(self.flags[flag])) for flag in all)

    @commands.hybrid_command(
        "user", description="⚒ Information about a user", help="[user]"
    )
    @app_commands.describe(member="Name of member")
    async def _user(
        self, ctx: Context, *, member: Optional[discord.Member] = None
    ) -> None:
        member = member or ctx.author

        avatar = get_asset_url(member.avatar)

        if member.premium_since is None:
            boosting = "`Not boosting.`"
        else:
            boosting = f"`Boosting` (`since` {discord.utils.format_dt(member.premium_since, 'R')})"

        if len(member.roles) == 1:
            roles = "`No roles.`"
        else:
            roles = ", ".join(role.mention for role in member.roles[1:][::-1])

        permissions = get_permissions(ctx.channel.permissions_for(member))

        await ctx.send(
            embed=Embed.default(
                description=f"""
➤ ID: `{member.id}`
➤ Created: {discord.utils.format_dt(member.created_at, "R")}
➤ Badges: {self.get_flags(member)}
        """
            )
            .add_field(
                name="Server",
                value=f"""
➤ Joined: {discord.utils.format_dt(member.joined_at, "R")}
➤ Boosting: {boosting}
➤ Roles: {roles}
➤ Permissions: {permissions}
        """,
            )
            .set_author(name=member, icon_url=avatar)
            .set_thumbnail(url=avatar),
            view=ui.View().add_item(
                ui.Button(style=ButtonStyle.link, label="Avatar", url=avatar)
            ),
        )

    @commands.hybrid_command("server", description="⚒ Information about the server")
    async def _server(self, ctx: Context) -> None:
        guild = ctx.guild

        icon = get_asset_url(guild.icon)
        members = guild.member_count
        humans = members - len(list(filter(lambda member: member.bot, guild.members)))
        bots = members - humans

        if len(guild.features) < 1:
            features = "No features."
        else:
            features = "".join(
                f":white_check_mark: {feature.replace('_', ' ').title()}\n"
                for feature in guild.features
            )

        await ctx.send(
            embed=Embed.default(
                description=f"""
{guild.description or "No description."}
                
➤ ID: `{guild.id}`
➤ Created: {discord.utils.format_dt(guild.created_at, "R")}
➤ Owner: {guild.owner.mention}
➤ Tier: `{guild.premium_tier}` (`{guild.premium_subscription_count:,} boosts`)
"""
            )
            .add_field(
                name="Basic",
                value=f"""
➤ Text Channels: `{len(guild.text_channels)}`
➤ Voice Channels: `{len(guild.voice_channels)}`
➤ Categories: `{len(guild.categories)}`
➤ Roles: `{len(guild.roles)}`""",
            )
            .add_field(
                name="Members",
                value=f"""
➤ Humans: `{humans:,}`
➤ Bots: `{bots:,}`
➤ Total Members: `{members:,}`""",
                inline=False,
            )
            .add_field(name="Features", value=features, inline=False)
            .set_author(name=guild.name, icon_url=icon)
            .set_thumbnail(url=icon),
            view=ui.View().add_item(
                ui.Button(style=ButtonStyle.link, label="Icon", url=icon)
            ),
        )

    @commands.hybrid_command(
        "emoji", description="⚒ Information about an emoji", help="<emoji>"
    )
    @app_commands.describe(emoji="Name of emoji")
    async def _emoji(self, ctx: Context, emoji: discord.Emoji) -> None:
        await ctx.send(
            embed=Embed.default(
                description=f"""
➤ ID: `{emoji.id}`
➤ Created: {discord.utils.format_dt(emoji.created_at, "R")}
➤ Animated? `{emoji.animated}`
➤ Mention: `{emoji}`
"""
            )
            .set_author(name=emoji.name, icon_url=emoji.url)
            .set_thumbnail(url=emoji.url),
            view=ui.View().add_item(
                ui.Button(style=ButtonStyle.link, label="Icon", url=emoji.url)
            ),
        )

    @commands.hybrid_command(
        "role", description="⚒ Information about a role", help="<role>"
    )
    @app_commands.describe(role="Name of role")
    async def _role(self, ctx: Context, role: discord.Role) -> None:
        with Image.new("RGB", (128, 128), role.color.to_rgb()) as image:
            buffer = BytesIO()
            image.save(buffer, "png")
            buffer.seek(0)

        embed = Embed.default(
            description=f"""
➤ ID: `{role.id}`
➤ Created: {discord.utils.format_dt(role.created_at, "R")}
➤ Permissions: {get_permissions(role.permissions)}
        """
        ).set_author(name=role.name, icon_url="attachment://color.png")

        if role.display_icon is not None:
            icon = get_asset_url(role.display_icon)
            embed.set_thumbnail(url=icon)
            await ctx.send(
                embed=embed,
                view=ui.View().add_item(
                    ui.Button(style=ButtonStyle.link, label="Icon", url=icon)
                ),
                file=discord.File(buffer, "color.png"),
            )
        else:
            await ctx.send(embed=embed, file=discord.File(buffer, "color.png"))

    @commands.hybrid_command(
        "pypi", description="⚒ Information about a PyPI package", help="<package>"
    )
    @app_commands.describe(package="Name of Pypi package")
    async def _pypi(self, ctx: Context, package: str) -> None:
        data = await (
            await self.bot.session.get(f"https://pypi.org/pypi/{package}/json")
        ).json()
        if "message" in data:
            raise Error(f"Package `{package}` not found.")
        info = data["info"]

        embed = Embed.default(
            title=f"{info['name']} | v{info['version']}",
            description=f"""
{info["summary"]}
            
➤ Author: `{info["author"]}`
➤ Python: `{info["requires_python"] if len(info["requires_python"]) > 0 else 'No requirement.'}`
➤ License: `{info["license"] if len(info["license"]) > 0 else 'No license.'}`
""",
        )

        if info["project_urls"] is not None:
            project_urls = ""
            for key, value in info["project_urls"].items():
                project_urls += f"➤ {key.title()}: [`{value}`]({value})\n"

            embed.add_field(name="Project Links", value=project_urls)

        await ctx.send(
            embed=embed,
            view=ui.View().add_item(
                ui.Button(style=ButtonStyle.link, label="View", url=info["project_url"])
            ),
        )

    @commands.hybrid_command(
        "snowflake", description="⚒ Information about a Discord id", help="<object>"
    )
    @app_commands.describe(object="Any discord ID")
    async def _snowflake(self, ctx: Context, object: discord.Object) -> None:
        await ctx.send(
            embed=Embed.default(
                title=object.type.__name__,
                description=f"""
➤ ID: `{object.id}`
➤ Created: {discord.utils.format_dt(object.created_at, "R")}
""",
            )
        )

    @commands.hybrid_command(
        "firstmessage",
        description="⚒ View the first message in a channel",
        help="[channel]",
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.describe(channel="Name of channel")
    async def _firstmessage(
        self, ctx: Context, *, channel: Optional[discord.TextChannel] = None
    ) -> None:
        channel = channel or ctx.channel

        message = await channel.history(oldest_first=True, limit=1).__anext__()

        await ctx.send(
            embed=Embed.default(
                description=f"""
➤ Channel: {channel.mention}
➤ Author: {message.author.mention}
➤ URL: [`jump`]({message.jump_url})
        """
            )
        )

    @commands.hybrid_command(
        "color", description="⚒ Information about a color", help="<color>"
    )
    @app_commands.describe(color="A color (attempts to parse RGB or HEX)")
    async def _color(self, ctx: Context, color: str):
        color = Color.parse(color)

        if not color:
            raise Error(f"Color `{color}` not found.")

        rgb = color.to_rgb()

        with Image.new("RGB", (128, 128), rgb) as image:
            buffer = BytesIO()
            image.save(buffer, "png")
            buffer.seek(0)

        await ctx.send(
            embed=Embed.default(
                description=f"""
➤ HEX: `#{color.to_hex()}`
➤ RGB: `{rgb[0]}, {rgb[1]}, {rgb[2]}`
"""
            ).set_thumbnail(url="attachment://color.png"),
            file=discord.File(buffer, "color.png"),
        )

    @commands.hybrid_command("randomcolor", description="⚒ Gets a random color")
    async def _randomcolor(self, ctx: Context):
        await self._color(
            ctx,
            f"{random.randint(0, 255)},{random.randint(0, 255)},{random.randint(0, 255)}",
        )
