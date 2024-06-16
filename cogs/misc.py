import os
import sys
import random
import logging
import requests
import datetime
import discord
from discord.ext import commands
from bs4 import BeautifulSoup

# Get the current and parent directories
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

# Append the parent directory to the system path
sys.path.append(parent_dir)

# Import from parent directory
import utils


class MiscCog(commands.Cog):
    """
    Miscellaneous commands that don't fit into other categories.
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        """
        Log statement to show cog loaded successfully.
        """
        logging.info('Misc Cog loaded.')


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
    

    @commands.command()
    async def game(self, ctx, *, args):
        '''User inputs game titles and the command returns a random title.'''
        logging.info('Game command submitted by [%s]', ctx.author.name)
        games: list[str] = args.split(',')

        if not games:
            await ctx.send("No game titles provided.")
            return

        random_choice = random.choice(games).strip()

        await ctx.send(f'You should play {random_choice}.')


    @commands.command()
    async def ufc(self, ctx):
        '''Scrapes ufc site for fight information.'''
        logging.info('Ufc command submitted by [%s]', ctx.author.name)

        url = 'https://www.espn.com/mma/schedule/_/league/ufc'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            date_html = soup.find_all('td', class_='date__col', limit=8)
            current_date = datetime.datetime.now()
            event_html = soup.find_all('td', class_='event__col', limit=4)

            embed = discord.Embed(title='', timestamp=current_date)
            embed.set_thumbnail(url='https://logos-world.net/wp-content/uploads/2021/02/Ultimate-Fighting-Championship-UFC-Logo.png')

            for i in range(0, len(date_html), 2):
                date_str = date_html[i].text
                event_date = datetime.datetime.strptime(date_str + " 2023", '%b %d %Y')
                date = event_date.strftime('%B %d')
                time = date_html[i + 1].text
                event_title = event_html[i // 2].text
                embed.add_field(name=event_title, value=f'{date} - {time} EST', inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send('Something went wrong...')


    @commands.command()
    async def elijah(self, ctx):
        """
        Returns amount of days since Elijah joined the military.
        """
        logging.info('Elijah command submitted by [%s]', ctx.author.name)
        siren_emoji = '\U0001F6A8'
        photo_url = 'https://i.ibb.co/1z8hNtS/IMG-7322.jpg'

        embed = discord.Embed(title=f'{siren_emoji} HE HAS RETURNED {siren_emoji}', timestamp=datetime.datetime.now())
        embed.set_image(url=photo_url)
        embed.add_field(name='Welcome back king.', value='', inline=False)

        await ctx.send(embed=embed)


    @commands.command()
    async def mark(self, ctx):
        """
        Returns amount of days since Mark left.
        """
        logging.info('Mark command submitted by [%s]', ctx.author.name)
        sad_emoji = '\U0001F62D'
        # file = discord.File('images/eli.png')

        day_eli_left = datetime.datetime(year=2024, month=4, day=16)
        today = datetime.datetime.now()
        difference = today - day_eli_left

        embed = discord.Embed(title="Days Since Mark Left", timestamp=datetime.datetime.now())
        embed.add_field(name='', value=f'{difference.days} days \t{sad_emoji}', inline=False)

        await ctx.send(embed=embed)


    @commands.command()
    async def updates(self, ctx):
        '''Bot changes and updates listed in embed.'''
        # Update timestamp each time new updates are posted
        embed = discord.Embed(title='GummyBot Updates', timestamp=datetime.datetime(year=2024, month=6, day=16, hour=9, minute=20))
        embed.set_footer(text='Changes to the bot were made at the following timestamp')
        embed.set_thumbnail(url='https://64.media.tumblr.com/84f68fd1ada52c9840b2dbe497f7eeb1/tumblr_ox2sd2eAXn1v64bqao5_r1_400.png')

        # Input changes made, adjust when new features added
        changes = [
            ['`$daily`', 'New command to earn points daily.'],
        ]

        for change in changes:
            embed.add_field(name=change[0], value=change[1], inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    """
    Allows Misc cog to be added to bot.
    """
    await bot.add_cog(MiscCog(bot))
