import asyncio
import functools
import io
import logging
import unicodedata
import random
import discord
import tabulate
import asyncio
import math
import os
import re
import random
import aiohttp
import discord

from discord.ext import commands
from redbot.core import Config, bank, checks, commands
from redbot.core.utils.chat_formatting import error, pagify, warning
from functools import partial


class Ars(commands.Cog):
    """Provides some weird commands"""

    def __init__(self, bot):
        self.bot = bot
        self.poll_sessions = []
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

    """Create polls using emoji reactions"""

    @commands.command(name="rpoll", pass_context=True, no_pm=True)
    async def rpoll(self, ctx, *text):
        """Starts/stops a reaction poll
        Usage example (time argument is optional, 60s is the default)
        rpoll Is this a poll?;Yes;No;Maybe;t=3d12h30m15s
        rpoll stop"""
        message = ctx.message
        channel = message.channel
        server = message.server
        if len(text) == 1:
            if text[0].lower() == "stop":
                await self.endpoll(message)
                return
        if not self.getPollByChannel(message):
            check = " ".join(text).lower()
            if "@everyone" in check or "@here" in check:
                await self.bot.say("Nice try.")
                return
            if not channel.permissions_for(server.me).manage_messages:
                await self.bot.say("I require the 'Manage Messages' "
                                   "permission in this channel to conduct "
                                   "a reaction poll.")
                return
            p = NewReactPoll(message, " ".join(text), self)
            if p.valid:
                self.poll_sessions.append(p)
                await p.start()
            else:
                await self.bot.say("`[p]rpoll question;option1;option2...;t=3d12h30m15s`")
        else:
            await self.bot.say("A reaction poll is already ongoing in this channel.")

    async def endpoll(self, message):
        if self.getPollByChannel(message):
            p = self.getPollByChannel(message)
            if p.author == message.author.id:  # or isMemberAdmin(message)
                await self.getPollByChannel(message).endPoll()
            else:
                await self.bot.say("Only admins and the author can stop the poll.")
        else:
            await self.bot.say("There's no reaction poll ongoing in this channel.")

    def getPollByChannel(self, message):
        for poll in self.poll_sessions:
            if poll.channel == message.channel:
                return poll
        return False

    async def check_poll_votes(self, message):
        if message.author.id != self.bot.user.id:
            if self.getPollByChannel(message):
                self.getPollByChannel(message).checkAnswer(message)

    async def reaction_listener(self, reaction, user):
        # Listener is required to remove bad reactions
        if user == self.bot.user:
            return  # Don't remove bot's own reactions
        message = reaction.message
        emoji = reaction.emoji
        if self.getPollByChannel(message):
            p = self.getPollByChannel(message)
            if message.id == p.message.id and not reaction.custom_emoji and emoji in p.emojis:
                # Valid reaction
                if user.id not in p.already_voted:
                    # First vote
                    p.already_voted[user.id] = str(emoji)
                    return
                else:
                    # Allow subsequent vote but remove the previous
                    await self.bot.remove_reaction(message, p.already_voted[user.id], user)
                    p.already_voted[user.id] = str(emoji)
                    return

    def __unload(self):
        for poll in self.poll_sessions:
            if poll.wait_task is not None:
                poll.wait_task.cancel()


class NewReactPoll():
    # This can be made a subclass of NewPoll()

    def __init__(self, message, text, main):
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.poll_sessions = main.poll_sessions
        self.duration = 60  # Default duration
        self.duration_text = "60s"  # Default duration text
        self.wait_task = None
        msg = [ans.strip() for ans in text.split(";")]
        # Detect optional duration parameter
        if len(msg[-1].strip().split("t=")) == 2:
            dur = msg[-1].strip().split("t=")[1]
            self.duration_text = dur
            day = re.search(r'([0-9]+)d', dur)
            hour = re.search(r'([0-9]+)h', dur)
            minute = re.search(r'([0-9]+)m', dur)
            sec = re.search(r'([0-9]+)s', dur)
            if dur.isdigit():
                self.duration = int(dur)
                self.duration_text = "{}s".format(dur)
            else:
                self.duration = 0
                if day:
                    self.duration += int(day.group(1))*24*60*60
                if hour:
                    self.duration += int(hour.group(1))*60*60
                if minute:
                    self.duration += int(minute.group(1))*60
                if sec:
                    self.duration += int(sec.group(1))
            msg.pop()
        # Reaction poll supports maximum of 9 answers and minimum of 2
        if len(msg) < 2 or len(msg) > 10:
            self.valid = False
            return None
        else:
            self.valid = True
        self.already_voted = {}
        self.question = msg[0]
        msg.remove(self.question)
        self.answers = {}  # Made this a dict to make my life easier for now
        self.emojis = []
        i = 1
        # Starting codepoint for keycap number emojis (\u0030... == 0)
        base_emoji = [ord('\u0030'), ord('\u20E3')]
        for answer in msg:  # {id : {answer, votes}}
            base_emoji[0] += 1
            self.emojis.append(chr(base_emoji[0]) + chr(base_emoji[1]))
            answer = self.emojis[i-1] + ' ' + answer
            self.answers[i] = {"ANSWER": answer, "VOTES": 0}
            i += 1
        self.message = None

    async def poll_wait(self):
        await asyncio.sleep(self.duration)
        if self.valid:
            await self.endPoll(expired=True)

    # Override NewPoll methods for starting and stopping polls
    async def start(self):
        msg = "**POLL STARTED!**\n\n{}\n\n".format(self.question)
        for id, data in self.answers.items():
            msg += "{}\n".format(data["ANSWER"])
        msg += ("\nSelect the number to vote!"
                "\nPoll closes in {}.".format(self.duration_text))
        self.message = await self.client.send_message(self.channel, msg)
        for emoji in self.emojis:
            await self.client.add_reaction(self.message, emoji)
            await asyncio.sleep(0.5)

        self.wait_task = self.client.loop.create_task(self.poll_wait())

    async def endPoll(self, expired=False):
        self.valid = False
        if not expired:
            self.wait_task.cancel()
        # Need a fresh message object
        self.message = await self.client.get_message(self.channel, self.message.id)
        msg = "**POLL ENDED!**\n\n{}\n\n".format(self.question)
        for reaction in self.message.reactions:
            if reaction.emoji in self.emojis:
                self.answers[ord(reaction.emoji[0]) -
                             48]["VOTES"] = reaction.count - 1
        await self.client.clear_reactions(self.message)
        cur_max = 0  # Track the winning number of votes
        # Double iteration probably not the fastest way, but works for now
        for data in self.answers.values():
            if data["VOTES"] > cur_max:
                cur_max = data["VOTES"]
        for data in self.answers.values():
            if cur_max > 0 and data["VOTES"] == cur_max:
                msg += "**{} - {} votes**\n".format(
                    data["ANSWER"], str(data["VOTES"]))
            else:
                msg += "*{}* - {} votes\n".format(
                    data["ANSWER"], str(data["VOTES"]))
        await self.client.send_message(self.channel, msg)
        self.poll_sessions.remove(self)
