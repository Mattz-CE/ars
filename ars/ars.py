import asyncio
import functools
import io
import logging
import unicodedata

import aiohttp
import discord
from redbot.core import commands
import lavalink


class Ars(commands.Cog):
    """Provides some weird commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.command(name="fuck", no_pm=True)
    async def fuck(self, ctx):
        channel = ctx.channel
        convert = False
        await ctx.send("Fuck you")
        await ctx.send("`Error in command 'fuck'. Click link to talk to the dev: https://bit.ly/3nhMjx5`")

    @commands.command(name="rr", no_pm=True)
    async def rr(self, ctx):
        channel = ctx.channel
        convert = False
        await ctx.send("https://www.youtube.com/watch?v=iik25wqIuFo")
        vc = ctx.vc
        link = "https://www.youtube.com/watch?v=iik25wqIuFo"
        try:
            player = lavalink.get_player(vc.guild.id)
        except KeyError:
            player = None
        if not player:
            try:
                player = await lavalink.connect(vc)
            except IndexError:
                return
        link = link[
            0
        ]  # could be rewritten to add ALL links, the tts backend is ready for it
        tracks = await player.load_tracks(query=link)
        if not tracks.tracks:
            if False:
                provider = voices[author_data["voice"]]["provider"]
                if provider == "Naver":
                    await channel.send("Something went wrong.")
                    return
                urls = await generate_urls(self, "Clara", text, author_data["speed"])
                link = urls[0]
                tracks = await player.load_tracks(query=link)
                if not tracks.tracks:
                    await channel.send("Something went wrong.")
                    return

            await channel.send(
                "Something went wrong. It's likely the SFX link is invalid."
            )
            return

        track = tracks.tracks[0]

        if player.current is None and not player.queue:
            player.queue.append(track)
            self.current_sfx[vc.guild.id] = track
            await player.play()
            return

        try:
            csfx = self.current_sfx[vc.guild.id]
        except KeyError:
            csfx = None

        if csfx is not None:
            player.queue.insert(0, track)
            await player.skip()
            self.current_sfx[vc.guild.id] = track
            return

        self.last_track_info[vc.guild.id] = (player.current, player.position)
        self.current_sfx[vc.guild.id] = track
        player.queue.insert(0, track)
        player.queue.insert(1, player.current)
        await player.skip()
