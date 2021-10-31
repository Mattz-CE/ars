import asyncio
import functools
import io
import logging
import unicodedata
import random

import aiohttp
import discord
from redbot.core import commands
from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import pagify


class Ars(commands.Cog):
    """Provides some weird commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

        default_config = {"king_dong": 134621854878007296}
        self._config = Config.get_conf(self, identifier=134621854878007300)
        self._config.register_global(**default_config)

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

    @commands.command(name="c", no_pm=True)
    async def c(self, ctx):
        """Starts a conversation with Ars bot"""

    @commands.command(name="penis", no_pm=True)
    async def penis(self, ctx, *users: discord.Member):
        """Detects user's penis length

        Enter multiple users for an accurate comparison!"""

        dongs = {}
        msg = ""
        state = random.getstate()
        king_dong = await self._config.king_dong()

        for user in users:
            random.seed(user.id)

            if user.id == king_dong:
                dong_size = 40
            else:
                dong_size = random.randint(0, 30)

            dongs[user] = "8{}D".format("=" * dong_size)

        random.setstate(state)
        dongs = sorted(dongs.items(), key=lambda x: x[1])

        for user, dong in dongs:
            msg += "**{}'s size:**\n{}\n".format(user.display_name, dong)

        for page in pagify(msg):
            await ctx.send(page)
