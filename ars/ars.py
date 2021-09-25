import asyncio
import functools
import io
import logging
import unicodedata

import aiohttp
import discord
from redbot.core import commands

try:
    import cairosvg

    svg_convert = "cairo"
except:
    try:
        from wand.image import Image

        svg_convert = "wand"
    except:
        svg_convert = None

log = logging.getLogger("red.ars.ars")


class Ars(commands.Cog):

    """Provides some weird commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        if svg_convert == "cairo":
            log.debug("Ars.py: Using CairoSVG for svg conversion.")
        elif svg_convert == "wand":
            log.debug("Ars.py: Using wand for svg conversion.")
        else:
            log.debug(
                "Ars.py: Failed to import svg converter. Standard emoji will be limited to 72x72 png.")

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.command(name="fuck")
    async def fuck(self, ctx, emoji):
        """Fuck (/fʌk/ fuhk) is a profane English-language word."""
        channel = ctx.channel
        convert = False
        await ctx.send("Fuck you")
