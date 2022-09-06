import datetime
from typing import Optional

import discord.utils
from discord import app_commands
from discord.ext import commands

from phyto.core.bot import Phyto
from phyto.core.context import Context
from phyto.core.embed import Embed
from phyto.core.exceptions import Error
from phyto.core.paginator import EmbedPaginatorMenu


class Fun(commands.Cog):
    def __init__(self, bot: Phyto) -> None:
        super().__init__()
        self.bot = bot
        self.icon = "🙂"
        self.christmas_day = datetime.datetime(2022, 12, 25)

    @commands.hybrid_command("christmas", description="🙂 Amount of days till Christmas")
    async def _christmas(self, ctx: Context) -> None:
        await ctx.send(
            embed=Embed.default(
                description=f"Christmas is {discord.utils.format_dt(self.christmas_day, 'R')}."
            )
        )

    async def send_reddit_embed(
        self, ctx: Context, url: str, *, subreddit: str = None
    ) -> None:
        allow_nsfw = ctx.channel.is_nsfw()

        posts = await (await self.bot.session.get(url)).json()

        if posts.get("code") == 404:
            raise Error(f"Subreddit `{subreddit}` contains no posts or does not exist.")

        if posts.get("code") == 400:
            raise Error(f"Subreddit `{subreddit}` contains no images.")

        posts = posts["memes"]

        embeds = [
            Embed.default(
                title=post["title"],
                url=post["postLink"],
                description=f"""
➤ Subreddit: `{post["subreddit"]}`
➤ Author: `{post["author"]}`
➤ Upvotes: `{post["ups"]:,}`
""",
            ).set_image(url=post["url"])
            for post in posts
            if allow_nsfw or (not allow_nsfw and not post["nsfw"])
        ]

        if len(embeds) < 1:
            raise Error(f"Subreddit `{subreddit}` has no valid posts.")

        await EmbedPaginatorMenu(ctx, embeds).start()

    @commands.hybrid_command("meme", description="🙂 Displays a random meme")
    @commands.cooldown(1, 15, commands.BucketType.user)
    @app_commands.describe(amount="Amount of memes")
    async def _meme(self, ctx: Context, *, amount: Optional[int] = 1) -> None:
        await self.send_reddit_embed(
            ctx, f"https://meme-api.herokuapp.com/gimme/{amount}"
        )

    @commands.hybrid_command(
        "reddit", description="🙂 Displays a random image from a subreddit"
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    @app_commands.describe(subreddit="Subreddit from reddit", amount="Amount of posts")
    async def _reddit(
        self, ctx: Context, subreddit: str, amount: Optional[int] = 1
    ) -> None:
        await self.send_reddit_embed(
            ctx,
            f"https://meme-api.herokuapp.com/gimme/{subreddit}/{amount}",
            subreddit=subreddit,
        )
