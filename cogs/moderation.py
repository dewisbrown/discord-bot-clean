import logging

import discord
from discord.ext import commands

import utils


class ModerationCog(commands.Cog):
    """
    Commands for discord moderation.
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        """
        Prints when cog is loaded.
        """
        logging.info('Moderation Cog loaded.')


async def setup(bot):
    """
    Adds moderation cog to bot.
    """
    await bot.add_cog(ModerationCog(bot))
