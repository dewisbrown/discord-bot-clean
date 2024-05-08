# GummyBot
## Overview
### About
GummyBot was created to use in a few servers that I'm active in. It started simple, but I've been slowly adding more features and commands. The bot is updated regularly and I'm always open to ideas for commands.
### Playback in Voice Channel
The main purpose of the bot is to allow audio playback in a voice channel. Users can submit YouTube or Spotify track links and the bot will playback the audio in whatever voice channel that you are in. There are many bots available online that provide this, but I wanted to make one of my own to avoid outages for maintenance.
### Battlepass
The secondary purpose of the bot is to maintain a _battlepass_ for users in the server. You can register for the battlepass, gain points, level up, and purchase items from a _shop_. These points, levels, and items have zero application, but it's there to give users something to do periodically.

## Code Structure
### Entry Point
`bot.py` is the entry point for the application. The client is instantiated and commands are loaded through _cogs_. The bot API key is also supplied here.
### Cogs
Cogs allow a way to organize commands into separate classes, depending on their funcitonality. For this bot, commands fall into one of the following cogs: `basics`, `battlepass`, `misc`, `moderation`, `music`, and `shop`. All cog classes are set up like this:
```
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def example_command(self, ctx):
        await ctx.send('Your command worked!')


async def setup(bot):
    await bot.add_cog(ExampleCog(bot))
```
### Commands
Looking at the code block above, you can see that commands use the `commands.command()` decorator. Also, each command includes the arg `ctx`, which represents the context in which a command is being invoked under. The Context class contains a lot of metadata, which can be read about [here](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Context). This is used to extract data like the author, channel, guild, and voice_client.
### Helper Modules
There are a few scripts in the root directory that are used throughout the cog files. `db_interface.py` provides functions for reading and writing to the database file for the bot. `download_yt.py` is used for extracting YouTube/Spotify data from links. `utils.py` contains various functions and constants used by cogs.