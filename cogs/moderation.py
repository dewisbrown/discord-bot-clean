import os
import sys
import logging
import discord
from discord.ext import commands

# Get the current and parent directories
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

# Append the parent directory to the system path
sys.path.append(parent_dir)

# Import from parent directory
import utils


class ModerationCog(commands.Cog):
    '''Commands for discord moderation.'''
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        '''Prints when cog is loaded.'''
        logging.info('Moderation Cog loaded.')


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
