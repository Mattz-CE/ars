import asyncio
import functools
import io
import logging
import unicodedata

import aiohttp
import discord
from redbot.core import commands


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
    async def fuck(self, *, ctx, text):
        channel = ctx.channel
        convert = False
        # await ctx.send("Fuck you")
        await self.bot.say("Fuck you")
