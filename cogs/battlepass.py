import sys
import os
import logging
import datetime

import discord
from discord.ext import commands

import db_interface as db

# Get the current and parent directories
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

# Append the parent directory to the system path
sys.path.append(parent_dir)

# Import from parent directory
import utils


class BattlepassCog(commands.Cog):
    """
    Commands to register for battlepass, collect points, increase level,
    and interact with item shop.
    """
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        """
        Print statment to ensure loads properly.
        """
        logging.info('Battlepass Cog loaded.')


    @commands.command()
    async def register(self, ctx):
        """
        Creates user in battlepass database.
        """
        logging.info('Register command submitted by [%s]', ctx.author.name)

        user_id = ctx.author.id
        user_name = ctx.author.name

        # added guild_id, not sure if needed
        # for maintaining user data in multiple servers
        guild_id = ctx.author.guild.id
        guild_name = ctx.author.guild.name

        registration_timestamp = datetime.datetime.now()
        daily_timestamp = datetime.datetime.now()

        user_exists = db.get_user_id(user_id=user_id)

        if user_exists:
            await ctx.send("You are already registered.")
        else:
            db.create_user(
                user_id=user_id,
                guild_id=guild_id,
                redemption_time=registration_timestamp,
                user_name=user_name,
                daily_redemption=daily_timestamp
                )

            embed = discord.Embed(title='Battlepass Registration', timestamp=registration_timestamp)
            embed.set_author(name=user_name, icon_url=ctx.author.avatar)
            embed.set_thumbnail(url='http://media.comicbook.com/2018/05/battle-pass-icon-1111187.jpeg')
            embed.add_field(name='', value='You have received 120 points for registering.', inline=False)
            await ctx.send(embed=embed)

            logging.info(
                '[%s:%s] successfully registered for battlepass in server [%s:%s].', 
                user_name, utils.decimal_to_hex(user_id), 
                guild_name, utils.decimal_to_hex(guild_id)
                )


    @commands.command()
    async def points(self, ctx):
        """
        Allows user to receive points every 15 minutes.
        """
        logging.info('Points command submitted by [%s]', ctx.author.name)
        user_id = ctx.author.id
        user_name = ctx.author.name
        guild_id = ctx.author.guild.id
        guild_name = ctx.author.guild.name

        redemption_time_str = db.retrieve_redemption_time(user_id=user_id)

        if redemption_time_str:
            last_redeemed = datetime.datetime.strptime(redemption_time_str, '%Y-%m-%d %H:%M:%S.%f')
            current_time = datetime.datetime.now()
            time_since_redemption = current_time - last_redeemed
            next_redemption_time = (last_redeemed + datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %I:%M %p')

            # Check if it has been at least 15 minutes
            if time_since_redemption.total_seconds() >= 900: # 15 minutes
                points = db.retrieve_points(user_id=user_id)
                level = db.retrieve_level(user_id=user_id)
                points_gained = utils.points(level=level)

                db.update_points(user_id=user_id, points=(points_gained + points))
                db.update_redemption_time(user_id=user_id, current_time=current_time)

                embed = discord.Embed(title='Battlepass Points', timestamp=current_time)
                embed.set_author(name=f'Requested by {user_name}', icon_url=ctx.author.avatar)
                embed.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/stack-of-coins/100/coin-03-512.png')
                embed.add_field(name=f'You\'ve been awarded {points_gained} points!', value=f'Updated points: {points + points_gained}', inline=False)
                embed.add_field(name='', value=f'Your next redemption time is: {(current_time + datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %I:%M %p")}', inline=False)
                await ctx.send(embed=embed)

                logging.info('Successfully awarded %d points to [%s:%s] in server [%s:%s].',
                             points_gained,
                             user_name, utils.decimal_to_hex(user_id),
                             guild_name, utils.decimal_to_hex(guild_id)
                            )

            else:
                embed = discord.Embed(title='Battlepass Points', timestamp=current_time)
                embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)
                embed.add_field(name='', value='Sorry, you can only claim points every 15 minutes.', inline=False)
                embed.add_field(name='', value=f'Your next redemption time is: {next_redemption_time}', inline=False)
                await ctx.send(embed=embed)

                logging.info(
                    '[%s:%s] attempted to earn points before correct time in server [%s:%s].', 
                    user_name, utils.decimal_to_hex(user_id), 
                    guild_name, utils.decimal_to_hex(guild_id)
                    )
        else:
            await ctx.send('You\'re not registered in the points system yet. Use the `$register` command to get started.')
            logging.info('[%s:%s] attempted to earn points without being registered to battlepass in server [%s:%s].',
                         user_name, utils.decimal_to_hex(user_id),
                         guild_name, utils.decimal_to_hex(guild_id)
                         )

    @commands.command()
    async def daily(self, ctx):
        """
        Allows user to receive points every 24 hours.
        """
        logging.info('Daily command submitted by [%s]', ctx.author.name)
        user_id = ctx.author.id
        user_name = ctx.author.name
        guild_id = ctx.author.guild.id
        guild_name = ctx.author.guild.name

        daily_redemption_str = db.retrieve_daily_redemption_time(user_id=user_id)

        if daily_redemption_str:
            last_redeemed = datetime.datetime.strptime(daily_redemption_str, '%Y-%m-%d %H:%M:%S.%f')
            current_time = datetime.datetime.now()
            time_since_redemption = current_time - last_redeemed
            next_redemption_time = (last_redeemed + datetime.timedelta(hours=24)).strftime('%Y-%m-%d %I:%M %p')

            # Check if it has been at least 24 hours
            if time_since_redemption.total_seconds() >= 86400: # 24 hours = 86400 seconds
                points = db.retrieve_points(user_id=user_id)
                points_gained = 100

                db.update_points(user_id=user_id, points=(points_gained + points))
                db.update_daily_redemption_time(user_id=user_id, current_time=current_time)

                embed = discord.Embed(title='Battlepass Points', timestamp=current_time)
                embed.set_author(name=f'Requested by {user_name}', icon_url=ctx.author.avatar)
                embed.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/stack-of-coins/100/coin-03-512.png')
                embed.add_field(name=f'You\'ve been awarded {points_gained} points!', value=f'Updated points: {points + points_gained}', inline=False)
                embed.add_field(name='', value=f'Your next redemption time is: {(current_time + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %I:%M %p")}', inline=False)
                await ctx.send(embed=embed)

                logging.info('Successfully awarded %d points to [%s:%s] in server [%s:%s].',
                             points_gained,
                             user_name, utils.decimal_to_hex(user_id),
                             guild_name, utils.decimal_to_hex(guild_id)
                            )
            else:
                embed = discord.Embed(title='Battlepass Points', timestamp=current_time)
                embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)
                embed.add_field(name='', value='Sorry, you can only claim daily points every 24 hours.', inline=False)
                embed.add_field(name='', value=f'Your next redemption time is: {next_redemption_time}', inline=False)
                await ctx.send(embed=embed)

                logging.info(
                    '[%s:%s] attempted to earn points before correct time in server [%s:%s].', 
                    user_name, utils.decimal_to_hex(user_id), 
                    guild_name, utils.decimal_to_hex(guild_id)
                    )
        else:
            await ctx.send('You\'re not registered in the points system yet. Use the `$register` command to get started.')
            logging.info('[%s:%s] attempted to earn points without being registered to battlepass in server [%s:%s].',
                         user_name, utils.decimal_to_hex(user_id),
                         guild_name, utils.decimal_to_hex(guild_id)
                         )

    @commands.command()
    async def tierup(self, ctx):
        """
        Allows the user to spend points to level up.
        """
        logging.info('Tierup command submitted by [%s]', ctx.author.name)
        user_id = ctx.author.id
        user_name = ctx.author.name
        guild_id = ctx.author.guild.id
        guild_name = ctx.author.guild.name

        current_level = db.retrieve_level(user_id=user_id)
        points = db.retrieve_points(user_id=user_id)

        if points:
            points_to_level_up = utils.points_to_level_up(current_level)
            embed = discord.Embed(title='Battlepass Tier Up', timestamp=datetime.datetime.now())
            embed.set_author(name=user_name, icon_url=ctx.author.avatar)

            if points >= points_to_level_up:
                db.update_level(user_id=user_id, level=(current_level + 1))
                db.update_points(user_id=user_id, points=(points - points_to_level_up))

                embed.set_thumbnail(url='https://res.cloudinary.com/teepublic/image/private/s--V423wCbg--/t_Resized%20Artwork/c_fit,g_north_west,h_954,w_954/co_000000,e_outline:48/co_000000,e_outline:inner_fill:48/co_ffffff,e_outline:48/co_ffffff,e_outline:inner_fill:48/co_bbbbbb,e_outline:3:1000/c_mpad,g_center,h_1260,w_1260/b_rgb:eeeeee/t_watermark_lock/c_limit,f_auto,h_630,q_90,w_630/v1535464012/production/designs/3077990_0.jpg')
                embed.add_field(name=f'You leveled up to level: {current_level + 1}', value=f'Points after tier up: {points - points_to_level_up}', inline=False)

                logging.info('[%s:%s] spent %s points to level up in server [%s:%s]',
                             user_name, utils.decimal_to_hex(user_id),
                             points_to_level_up,
                             guild_name, utils.decimal_to_hex(guild_id)
                            )
                await ctx.send(embed=embed)
            else:
                embed.add_field(name=f'You need {points_to_level_up} points to level up.', value=f'Your points: {points}', inline=False)
                logging.info('[%s:%s] denied tierup in server [%s:%s]',
                             user_name, utils.decimal_to_hex(user_id),
                             guild_name, utils.decimal_to_hex(guild_id)
                            )
                await ctx.send(embed=embed)
        else:
            await ctx.send('You\'re not registered in the database yet. Use `$register` to enter yourself.')


    @commands.command()
    async def battlepass(self, ctx, user=None):
        """
        Returns the users current level and points.
        """
        logging.info('Battlepass command submitted by [%s]', ctx.author.name)
        user_id = ctx.author.id
        guild_name = ctx.author.guild.name

        if user:
            # Check if user is in same guild as ctx.author
            user_id = db.get_user_id(user_name=user, guild_id=ctx.author.guild.id)
            if user_id:
                user_id = int(user_id[0])
                points = db.retrieve_points(user_id=user_id)
                level = db.retrieve_level(user_id=user_id)
                if points:
                    embed = discord.Embed(title=f'[{guild_name}] Battlepass Progress', timestamp=datetime.datetime.now())
                    embed.set_author(name=user)
                    embed.add_field(name=f'Level: {level}', value=f'Points: {points}', inline=False)

                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f'{user} is not registered in the battlepass yet.')
            else:
                await ctx.send(f'`{user}` is either not in this guild or has not registered for the battlepass.')
        else:
            # Get user points and level
            points = db.retrieve_points(user_id=user_id)
            level = db.retrieve_level(user_id=user_id)

            if points:
                embed = discord.Embed(title=f'[{guild_name}] Battlepass Progress', timestamp=datetime.datetime.now())
                embed.set_author(name=ctx.author.name)
                embed.set_thumbnail(url=ctx.author.avatar)
                embed.add_field(name=f'Level: {level}', value=f'Points: {points}', inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send('You\'re not registered in the battlepass yet. Use the `$register` command to get started.')


    @commands.command()
    async def top5(self, ctx):
        """
        Returns the top 5 battlepass members.
        """
        logging.info('Top5 command submitted by [%s]', ctx.author.name)
        guild_id = int(ctx.author.guild.id)

        embed = discord.Embed(title='Top 5 Battlepass Members', description='Sorted by level and points.', timestamp=datetime.datetime.now())
        embed.set_thumbnail(url='https://ih1.redbubble.net/image.660900869.4748/pp,504x498-pad,600x600,f8f8f8.u8.jpg')

        results = db.retrieve_top_five(guild_id=guild_id)
        for result in results:
            user_name, level, points = result
            embed.add_field(name=user_name, value=f'Level: {level} Points: {points}', inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BattlepassCog(bot))
