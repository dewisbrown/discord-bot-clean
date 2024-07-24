import logging
import discord
import pytz
import datetime
from discord.ext import commands

class BasicsCog(commands.Cog):
    """
    Organizational class for basic commands.
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        """
        Log statment to show Basics cog loaded successfully.
        """
        logging.info('Basics Cog loaded.')


    @commands.command()
    async def hello(self, ctx):
        """
        Test command, replies hello!
        """
        await ctx.send('Hello, I am your Discord bot!')


    @commands.command()
    async def age(self, ctx, user: discord.Member = None):
        """
        Returns days since joining server.
        """
        if user is None:
            user = ctx.author

        if ctx.guild:
            joined_at = user.joined_at
            timezone = pytz.timezone('America/Chicago')

            # Convert joined_at to the server's timezone
            joined_at = joined_at.astimezone(timezone)

            current_time = datetime.datetime.now(timezone)
            days_in_server = (current_time - joined_at).days

            await ctx.send(f'{user.display_name} has been in the server {days_in_server} days.')
        else:
            await ctx.send('This command is only applicable in a server (guild) context')


async def setup(bot):
    await bot.add_cog(BasicsCog(bot))
