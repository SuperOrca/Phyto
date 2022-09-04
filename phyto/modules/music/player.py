import asyncio
from random import randrange

import discord
import wavelink
from wavelink import Track

from phyto.core.embed import Embed


class Player(wavelink.Player):
    def __init__(self, client: discord.Client, channel: discord.VoiceChannel):
        super().__init__(client, channel)
        self.queue = []
        self.source_channel = None
        self.loop = False
        self.shuffle = False
        self.skip = False

    async def next(self, players: dict):
        if self.skip:
            return
        elif len(self.channel.voice_states) < 2:
            await self.disconnect()
            await self.source_channel.send(
                embed=Embed.error(
                    description="Bot disconnected because there were no users connected."
                )
            )
            del players[self.guild.id]
        elif len(self.queue) < 1:
            await self.stop()
            wait = 0
            while True:
                if not self.is_connected():
                    return
                elif self.is_playing():
                    return
                else:
                    wait += 1
                    if wait >= 180:
                        await self.disconnect()
                        await self.source_channel.send(
                            embed=Embed.error(
                                description="Bot disconnected because no songs were played in the last `3 minutes`."
                            )
                        )
                        del players[self.guild.id]
                        break
                    await asyncio.sleep(1)
        else:
            self.skip = True
            track = self.get_track()

            await self.play(track)
            await self.source_channel.send(
                embed=Embed.default(
                    description=f"Now playing [`{track.title}`]({track.uri})."
                )
            )
            self.skip = False

    def get_track(self) -> Track:
        if not self.shuffle:
            track = self.queue[0]
            del self.queue[0]
            if self.loop:
                self.queue.append(track)
        else:
            index = randrange(len(self.queue))
            track = self.queue[index]
            del self.queue[index]
            if self.loop:
                self.queue.append(track)

        return track
