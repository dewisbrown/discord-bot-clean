"""

"""
import os, logging, asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()

# Logging setup
LOG_PATH = os.getenv('LOG_PATH')
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s [Line: %(lineno)d <%(filename)s>]',
                    datefmt='%I:%M:%S %p',
                    level=logging.INFO)

file_handler = logging.FileHandler(LOG_PATH)
file_handler.setFormatter((logging.Formatter(
                    '[%(asctime)s] %(levelname)s: %(message)s [Line: %(lineno)d <%(filename)s>]',
                    datefmt='%I:%M:%S %p')))
logging.getLogger().addHandler(file_handler)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.presences = True

bot = commands.Bot(command_prefix='$', intents=intents)

# Remove default help command
bot.remove_command('help')

@bot.event
async def on_ready():
    """
    Prints statment when bot is logged in.
    """
    logging.info('Success! Logged in as %s', bot.user.name)


@bot.event
async def on_command_error(ctx, error):
    """
    Sends error message to user when command is not found.
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found. Type `$help` for a list of commands.')
        logging.error('User input command that does not exist.')


async def load():
    """
    Loads cogs for bots.
    """
    cogs_directory = os.path.join(os.path.dirname(__file__), 'cogs')
    cog_files = [f.split('.')[0] for f in os.listdir(cogs_directory) if f.endswith('.py')]

    for cog in cog_files:
        if cog == 'music':
            await bot.load_extension(f'cogs.{cog}')


async def main():
    """
    Loads cogs and starts the bot login.
    """
    async with bot:
        await load()
        await bot.start(os.getenv('BOT_TOKEN'))

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('\nSession terminated...')
