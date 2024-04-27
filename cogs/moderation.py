import os
import sys
import datetime
import logging
import discord
import requests
from discord.ext import commands
from bs4 import BeautifulSoup

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


    @commands.command()
    async def help(self, ctx, command: str=None):
        """
        If a command name is submitted with this command,
        help for the command is returned. No command returns
        a list of all commands.
        """
        logging.info('Help command submitted by [%s]', ctx.author.name)

        embed = discord.Embed(timestamp=datetime.datetime.now())

        if command:
            info = utils.command_info(command=command)
            if info:
                embed = discord.Embed(title=f'Command Help - {command.capitalize()}', description=info['description'])
                embed.add_field(name='Command syntax', value=info['syntax'], inline=False)
                embed.add_field(name='Example', value=info['example'], inline=False)
            else:
                await ctx.send(f'There is no command `${command}`. Submit `$help` to see list of commands.')
        else:
            battlepass_commands = f'''`$battlepass` - {utils.command_info('battlepass')['description']}\n
                        `$points` - {utils.command_info('points')['description']}\n
                        `$register` - {utils.command_info('register')['description']}\n
                        `$tierup` - {utils.command_info('tierup')['description']}\n
                        `$top5` - {utils.command_info('top5')['description']}'''

            shop_commands = f'''`$buy` - {utils.command_info('buy')['description']}\n
                        `$inventory` - {utils.command_info('inventory')['description']}\n
                        `$shop` - {utils.command_info('shop')['description']}\n
                        `$submit_item` - {utils.command_info('submit_item')['description']}'''

            music_commands = f'''`$play` - {utils.command_info('play')['description']}\n
                        `$queue` - {utils.command_info('queue')['description']}\n
                        `$stop` - {utils.command_info('stop')['description']}\n'''

            misc_commands = f'''`$game` - {utils.command_info('game')['description']}\n
                        `$discordstatus` - {utils.command_info('discordstatus')['description']}\n
                        `$age` - {utils.command_info('age')['description']}\n
                        `$updates` - {utils.command_info('updates')['description']}\n
                        `$ufc` - {utils.command_info('ufc')['description']}\n
                        `$elijah` - {utils.command_info('elijah')['description']}\n
                        `$mark` - {utils.command_info('mark')['description']}'''

            # All commands
            embed.title = 'Command Help'
            embed.description = 'List of all bot commands. Use `$help <command>` for more information on each command.'
            embed.add_field(name='Battlepass Commands', value=battlepass_commands, inline=False)
            embed.add_field(name='', value='', inline=False)
            embed.add_field(name='Shop Commands', value=shop_commands, inline=False)
            embed.add_field(name='', value='', inline=False)
            embed.add_field(name='Music Commands', value=music_commands, inline=False)
            embed.add_field(name='', value='', inline=False)
            embed.add_field(name='Misc Commands', value=misc_commands, inline=False)
            embed.add_field(name='', value='', inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def discordstatus(self, ctx):
        '''Displays status of discord voice (US/East, US/Central)'''
        logging.info('discordstatus command submitted by [%s]', ctx.author.name)

        # Define the URL of the Discord Status page
        url = "https://discordstatus.com/"

        # Send a GET request to the website
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the div elements containing server information
            server_divs = soup.find_all('div', class_='component-inner-container')

            # Define dictionaries to store server statuses
            server_statuses = {}

            for server_div in server_divs:
                # Extract server name and status
                server_name = server_div.find('span', class_='name').text.strip()
                server_status = server_div.find('span', class_='component-status').text.strip()

                # Store server status in the dictionary
                server_statuses[server_name] = server_status

            # Build embed
            embed = discord.Embed(title='Discord Voice Status', timestamp=datetime.datetime.now(), url='https://discordstatus.com/')
            embed.set_thumbnail(url='https://logodownload.org/wp-content/uploads/2017/11/discord-logo-0.png')
            embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)

            # Check if the US East server is 'Operational'
            if 'US East' in server_statuses:
                embed.add_field(name='US East', value=server_statuses["US East"])

            # Check if the US Central server is 'Operational'
            if 'US Central' in server_statuses:
                embed.add_field(name='US Central', value=server_statuses["US Central"])

            await ctx.send(embed=embed)
        else:
            await ctx.send('US East and US Central status could not be found.')
            logging.error('Web scrape for discordstatus.com unsuccesful.')


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
