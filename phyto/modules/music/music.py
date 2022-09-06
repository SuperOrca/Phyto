import datetime
from typing import Optional

import discord
import humanize
import wavelink
from discord import ui, ButtonStyle, app_commands
from discord.ext import commands
from wavelink import Track

from phyto.core.bot import Phyto
from phyto.core.config import CONFIG
from phyto.core.context import Context
from phyto.core.embed import Embed
from phyto.core.exceptions import Error
from phyto.core.helpers import chunks
from phyto.core.paginator import EmbedPaginatorMenu
from .player import Player


class Music(commands.Cog):
    def __init__(self, bot: Phyto):
        self.bot = bot
        self.icon = "🎵"

        bot.loop.create_task(self.connect_nodes())
        self.players = {}

    async def connect_nodes(self):
        await self.bot.wait_until_ready()

        for node in CONFIG["lavalink"]:
            await wavelink.NodePool.create_node(
                bot=self.bot,
                host=node["host"],
                port=node["port"],
                password=node["password"],
                https=True,
            )

    async def get_player(self, ctx: Context) -> Player:
        if ctx.guild.id not in self.players:
            raise Error("Bot is not connected to any channel.")

        player = self.players[ctx.guild.id]

        if not ctx.author.voice or ctx.author.voice.channel != player.channel:
            raise Error("You are not in the same channel as the bot.")

        return player

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        self.bot.logger.info(f"Node {node.host} (ID: {node.identifier}) connected.")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: Player, track: Track, reason: str):
        await player.next(self.players)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member == self.bot.user and after.channel is None:
            if player := self.players.pop(member.guild.id, False):
                await player.disconnect()

    @commands.hybrid_command(
        "connect", description="🎵 Connect the bot to a channel", help="[channel]"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.describe(channel="Name of voice channel")
    async def _connect(
        self, ctx: Context, *, channel: Optional[discord.VoiceChannel] = None
    ) -> None:
        if ctx.guild.id in self.players:
            raise Error("Bot is already connected to a different channel.")

        if not channel or not ctx.author.voice:
            raise Error("Please join or specify a channel to connect to.")

        channel = channel or ctx.author.voice.channel

        player = await channel.connect(cls=Player)
        player.source_channel = ctx.channel
        self.players[ctx.guild.id] = player
        await ctx.send(
            embed=Embed.default(description=f"Bot connected to {channel.mention}.")
        )

    @commands.hybrid_command("pause", description="🎵 Pauses the current song")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _pause(self, ctx: Context) -> None:
        player = await self.get_player(ctx)

        if not player.is_playing():
            raise Error("Bot is not playing anything.")

        if player.is_paused():
            raise Error("Bot is already paused.")

        await player.pause()
        await ctx.send(embed=Embed.default(description="Bot paused."))

    @commands.hybrid_command("resume", description="🎵 Resumes the current song")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _resume(self, ctx: Context) -> None:
        player = await self.get_player(ctx)

        if not player.is_playing():
            raise Error("Bot is not playing anything.")

        if not player.is_paused():
            raise Error("Bot is already playing.")

        await player.resume()
        await ctx.send(embed=Embed.default(description="Bot resumed."))

    @commands.hybrid_command(
        "stop",
        description="🎵 Disconnects the bot from the channel",
        aliases=["disconnect"],
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _stop(self, ctx: Context) -> None:
        player = await self.get_player(ctx)

        await player.disconnect()
        del self.players[ctx.guild.id]
        await ctx.send(embed=Embed.default(description="Bot disconnected."))

    @commands.hybrid_command("skip", description="🎵 Skips the current song")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _skip(self, ctx: Context) -> None:
        player = await self.get_player(ctx)

        await ctx.send(embed=Embed.default(description="Song skipped."))
        await player.next(self.players, force=True)

    @commands.hybrid_command(
        "queue", description="🎵 View the queue of the bot", aliases=["q"]
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _queue(self, ctx: Context) -> None:
        player = await self.get_player(ctx)
        queue = player.queue
        current = player.track

        if len(queue) < 1:
            raise Error("The bot's queue is empty.")

        embeds = []
        index = 1

        for chunk in chunks(queue, 5):
            next = ""
            for track in chunk:
                next += f"{index}. [`{track.title}`]({track.uri})\n"
                index += 1
            embeds.append(
                Embed.default(
                    title="Queue",
                    fields=(
                        ("Now Playing", f"[`{current.title}`]({current.uri})"),
                        ("Next Up", next),
                    ),
                )
            )

        await EmbedPaginatorMenu(ctx, embeds).start()

    @commands.hybrid_command(
        "now", description="🎵 View the queue of the bot", aliases=["np", "playing"]
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _now(self, ctx: Context) -> None:
        player = await self.get_player(ctx)
        track = player.track

        duration = humanize.precisedelta(datetime.timedelta(seconds=track.duration))

        await ctx.send(
            embed=Embed.default(
                title=track.title,
                description=f"""
➤ Author: `{track.author}`
➤ Duration: `{duration}`
""",
            ).set_thumbnail(url=track.thumbnail),
            view=ui.View().add_item(
                ui.Button(style=ButtonStyle.link, label="View", url=track.uri)
            ),
        )

    @commands.hybrid_command(
        "remove", description="🎵 Remove a song from queue by index", help="<index>"
    )
    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.describe(index="Index of song in queue")
    async def _remove(self, ctx: Context, index: int) -> None:
        player = await self.get_player(ctx)
        index -= 1

        try:
            track = player.queue[index]
            del player.queue[index]
            await ctx.send(
                embed=Embed.default(
                    description=f"Removed [`{track.title}`]({track.uri}) from the queue."
                )
            )
        except IndexError:
            await ctx.send(
                embed=Embed.default(description=f"Index `{index}` not found.")
            )

    @commands.hybrid_command("loop", description="🎵 Loops the queue of the bot")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _loop(self, ctx: Context) -> None:
        player = await self.get_player(ctx)

        player.loop = not player.loop
        await ctx.send(
            embed=Embed.default(
                description=f"Bot is `{'now' if player.loop else 'no longer'}` looping."
            )
        )

    @commands.hybrid_command("volume", description="🎵 Set the volume of the bot")
    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.describe(volume="Volume of bot (1% to 1000%)")
    async def _volume(self, ctx: Context, volume: int) -> None:
        player = await self.get_player(ctx)

        if not 0 < volume <= 1000:
            raise Error(f"Volume `{volume}` cannot be less than 1 or greater than 100.")

        await player.set_volume(volume)
        await ctx.send(embed=Embed.default(description=f"Volume set to `{volume}%`."))

    @commands.hybrid_command("seek", description="🎵 Seek to part of song in seconds")
    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.describe(seconds="Number of seconds to skip to")
    async def _seek(self, ctx: Context, seconds: int) -> None:
        player = await self.get_player(ctx)
        track = player.track

        if not 0 < seconds < track.duration:
            raise Error(f"Position `{seconds}` is out of range.")

        await player.seek(seconds * 1000)
        await ctx.send(
            embed=Embed.default(
                description=f"Sought to `{humanize.precisedelta(datetime.timedelta(seconds=seconds))}`."
            )
        )

    @commands.hybrid_command("shuffle", description="🎵 Shuffles the queue of the bot")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def _shuffle(self, ctx: Context) -> None:
        player = await self.get_player(ctx)

        player.shuffle = not player.shuffle
        await ctx.send(
            embed=Embed.default(
                description=f"Bot is `{'now' if player.shuffle else 'no longer'}` shuffling."
            )
        )

    @commands.hybrid_command("play", description="🎵 Plays a song")
    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.describe(query="Name of song")
    async def _play(self, ctx: Context, query: wavelink.YouTubeMusicTrack) -> None:
        if query.is_stream():
            raise Error("Bot cannot play streams.")

        if ctx.guild.id not in self.players:
            if not ctx.author.voice:
                raise Error("Please join a channel to connect to.")
            channel = ctx.author.voice.channel

            player = await channel.connect(cls=Player)
            player.source_channel = ctx.channel
            self.players[ctx.guild.id] = player

        player = await self.get_player(ctx)

        if player.is_playing():
            if query.duration > 600:
                raise Error("Song is longer than `10 minutes`.")

            if len(player.queue) > 100:
                raise Error("You can only have `100` songs in queue.")

            player.queue.append(query)
            await ctx.send(
                embed=Embed.default(
                    description=f"Enqueued [`{query.title}`]({query.uri})."
                )
            )
        else:
            await player.play(query)
            await ctx.send(
                embed=Embed.default(
                    description=f"Now playing [`{query.title}`]({query.uri})."
                )
            )
