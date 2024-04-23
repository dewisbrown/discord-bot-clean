import logging
import random
import discord
import pytz
import datetime
import requests
from bs4 import BeautifulSoup
from discord.ext import commands

class BasicsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('Basics Cog loaded.')


    @commands.command()
    async def hello(self, ctx):
        '''Test command, replies hello!'''
        await ctx.send('Hello, I am your Discord bot!')


    @commands.command()
    async def age(self, ctx, user: discord.Member = None):
        '''Returns days since joining server.'''
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
    

    @commands.command()
    async def game(self, ctx, *args):
        '''User inputs game titles and the command returns a random title.'''
        logging.info('Game command submitted by [%s]', ctx.author.name)
        games = list(args)

        if not games:
            await ctx.send("No game titles provided.")
            return

        random_choice = random.choice(games)

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
        sad_emoji = '\U0001F62D'
        # file = discord.File('images/eli.png')

        day_eli_left = datetime.datetime(year=2024, month=3, day=26)
        today = datetime.datetime.now()
        difference = today - day_eli_left

        embed = discord.Embed(title="Days Since Elijah Left", timestamp=datetime.datetime.now())
        embed.add_field(name='', value=f'{difference.days} days \t{sad_emoji}', inline=False)

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
        embed = discord.Embed(title='GummyBot Updates', timestamp=datetime.datetime(year=2023, month=11, day=20, hour=9, minute=45))
        embed.set_footer(text='Changes to the bot were made at the following timestamp')
        embed.set_thumbnail(url='https://64.media.tumblr.com/84f68fd1ada52c9840b2dbe497f7eeb1/tumblr_ox2sd2eAXn1v64bqao5_r1_400.png')

        # Input changes made, adjust when new features added
        changes = [
            ['`$elijah`', 'See how many days it has been since Elijah joined.'],
            ['`$mark`', 'See how many days it has been since Mark left.'],
            ['`$updates`', 'Displays recent updates made to the bot.']
        ]

        for change in changes:
            embed.add_field(name=change[0], value=change[1], inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BasicsCog(bot))
