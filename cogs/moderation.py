import datetime
import logging
import discord
import requests
from discord.ext import commands
from bs4 import BeautifulSoup

class ModerationCog(commands.Cog):
    '''Commands for discord moderation.'''
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        '''Prints when cog is loaded.'''
        logging.info('Moderation Cog loaded.')

    # TODO: Add arg for help() to display embed for each command.
        # example: $help points
        # bot returns embed similar to submit_item embed already made
        # in battlepass cog
    @commands.command()
    async def help(self, ctx):
        '''Lists bot commands.'''
        embed = discord.Embed(timestamp=datetime.datetime.now())

        battlepass_commands = '''`$battlepass` - Displays level and points for user.\n
                    `$points` - Gain points every 15 minutes.\n
                    `$register` - Register for battlepass.\n
                    `$tierup` - Spend points to increase battlepass level.\n
                    `$top5` - Displays top 5 battlepass members.'''

        shop_commands = '''`$buy <item_name>` - Purchase item from item shop.\n
                    `$inventory` - Displays user inventory.\n
                    `$shop` - Displays shop items and values, refreshes every thirty minutes.'''

        music_commands = '''`$play <youtube_url>` - Plays supplied YouTube video audio in voice channel.\n
                    `$play <search_terms>` - Plays first search result of YouTube video audio in voice channel.\n
                    `$queue` - Displays the music queue.\n
                    `$stop` - Stops the music player and the bot exits the voice channel.\n'''

        misc_commands = '''`$game <title1> <title2> ...` - Bot selects random game title out of provided game titles.\n
                    `$age` - Displays user time since joining server.\n
                    `$updates` - Displays recent changes made to GummyBot.\n
                    `$ufc` - Displays next four UFC event dates, times, and titles.\n
                    `$elijah` - Displays days since Elijah joined.\n
                    `$mark` - Displays days since Mark joined.'''

        # All commands
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
