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
    '''Commands to register for battlepass, collect points, and increase tier level with points.'''
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        '''Print statment to ensure loads properly.'''
        logging.info('Battlepass Cog loaded.')


    @commands.command()
    async def register(self, ctx):
        '''Enters user into battlepass database.'''
        logging.info('Register command submitted by [%s]', ctx.author.name)

        user_id = ctx.author.id
        user_name = ctx.author.name

        # added guild_id, not sure if needed
        # for maintaining user data in multiple servers
        guild_id = ctx.author.guild.id
        guild_name = ctx.author.guild.name
        logging.info('Guild name : [%s]', guild_name)
        registration_timestamp = datetime.datetime.now()

        user_exists = db.get_user_id(user_id=user_id)

        if user_exists:
            await ctx.send("You are already registered.")
        else:
            db.add_user(
                user_id=user_id,
                guild_id=guild_id,
                last_awarded_at=registration_timestamp,
                user_name=user_name
                )

            embed = discord.Embed(title='Battlepass Registration', timestamp=registration_timestamp)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
            embed.set_thumbnail(url='http://media.comicbook.com/2018/05/battle-pass-icon-1111187.jpeg')
            embed.add_field(name='', value='You have received 20 points for registering.', inline=False)
            await ctx.send(embed=embed)

            logging.info(
                '[%s:%s] successfully registered for battlepass in server [%s:%s].', 
                user_name, utils.decimal_to_hex(user_id), 
                guild_name, utils.decimal_to_hex(guild_id)
                )


    @commands.command()
    async def points(self, ctx):
        '''Allows user to get points every 15 minutes.'''
        logging.info('Points command submitted by [%s]', ctx.author.name)
        user_id = ctx.author.id

        last_awarded_at_str = db.get_last_awarded_at(user_id=user_id)

        if last_awarded_at_str:
            last_awarded_at = datetime.datetime.strptime(last_awarded_at_str, '%Y-%m-%d %H:%M:%S.%f')
            current_time = datetime.datetime.now()
            time_since_last_awarded = current_time - last_awarded_at
            next_redemption_time = (last_awarded_at + datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %I:%M %p')

            # Check if it has been at least 15 minutes
            if time_since_last_awarded.total_seconds() >= 900: # 15 minutes
                level = db.get_level(user_id=user_id)
                points = db.get_points(user_id=user_id)
                points_to_increment = get_points_for_command(level)

                db.set_points(user_id=user_id, points=(points_to_increment + points))
                db.set_last_awarded_at(user_id=user_id, current_time=current_time)

                embed = discord.Embed(title='Battlepass Points', timestamp=current_time)
                embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)
                embed.set_thumbnail(url='https://cdn4.iconfinder.com/data/icons/stack-of-coins/100/coin-03-512.png')
                embed.add_field(name=f'You\'ve been awarded {points_to_increment} points!', value=f'Updated points: {points + points_to_increment}', inline=False)
                embed.add_field(name='', value=f'Your next redemption time is: {(current_time + datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %I:%M %p")}', inline=False)
                await ctx.send(embed=embed)

                logging.info('Successfully awarded %d points to [%s].', points_to_increment, ctx.author.name)

            else:
                embed = discord.Embed(title='Battlepass Points', timestamp=current_time)
                embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)
                embed.add_field(name='', value='Sorry, you can only claim points every 15 minutes.', inline=False)
                embed.add_field(name='', value=f'Your next redemption time is: {next_redemption_time}', inline=False)
                await ctx.send(embed=embed)

                logging.info('[%s] attempted to earn points before correct time.', ctx.author.name)
        else:
            await ctx.send('You\'re not registered in the points system yet. Use the `$register` command to get started.')
            logging.info('[%s] attempted to earn points without being registered to battlepass.', ctx.author.name)


    @commands.command()
    async def tierup(self, ctx):
        '''Allows the user to spend points to level up.'''
        logging.info('Tierup command submitted by [%s]', ctx.author.name)
        user_id = ctx.author.id

        current_level = db.get_level(user_id=user_id)
        points = db.get_points(user_id=user_id)

        if points:
            points_to_level_up = get_points_to_level(current_level)
            embed = discord.Embed(title='Battlepass Tier Up', timestamp=datetime.datetime.now())
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)

            if points >= points_to_level_up:
                db.set_level(user_id=user_id, level=(current_level + 1))
                db.set_points(user_id=user_id, points=(points - points_to_level_up))

                embed.set_thumbnail(url='https://res.cloudinary.com/teepublic/image/private/s--V423wCbg--/t_Resized%20Artwork/c_fit,g_north_west,h_954,w_954/co_000000,e_outline:48/co_000000,e_outline:inner_fill:48/co_ffffff,e_outline:48/co_ffffff,e_outline:inner_fill:48/co_bbbbbb,e_outline:3:1000/c_mpad,g_center,h_1260,w_1260/b_rgb:eeeeee/t_watermark_lock/c_limit,f_auto,h_630,q_90,w_630/v1535464012/production/designs/3077990_0.jpg')
                embed.add_field(name=f'You leveled up to level: {current_level + 1}', value=f'Points after tier up: {points - points_to_level_up}', inline=False)
                await ctx.send(embed=embed)
            else:
                embed.add_field(name=f'You need {points_to_level_up} points to level up.', value=f'Your points: {points}', inline=False)
                await ctx.send(embed=embed)
        else:
            await ctx.send('You\'re not registered in the database yet. Use `$register` to enter yourself.')


    @commands.command()
    async def battlepass(self, ctx):
        '''Returns the users current level and points.'''
        logging.info('Battlepass command submitted by [%s]', ctx.author.name)
        user_id = ctx.author.id

        # Get user points and level
        points = db.get_points(user_id=user_id)
        level = db.get_level(user_id=user_id)

        if points:
            embed = discord.Embed(title='Battlepass Progress', timestamp=datetime.datetime.now())
            embed.set_author(name=ctx.author.name)
            embed.set_thumbnail(url=ctx.author.avatar)
            embed.add_field(name=f'Level: {level}', value=f'Points: {points}', inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send('You\'re not registered in the points system yet. Use the `$register` command to get started.')


    @commands.command()
    async def top5(self, ctx):
        '''Returns the top 5 battlepass members.'''
        logging.info('Top5 command submitted by [%s]', ctx.author.name)
        embed = discord.Embed(title='Top 5 Battlepass Members', description='Sorted by level and points.', timestamp=datetime.datetime.now())
        embed.set_thumbnail(url='https://ih1.redbubble.net/image.660900869.4748/pp,504x498-pad,600x600,f8f8f8.u8.jpg')

        results = db.get_top_five()
        for result in results:
            user_name, level, points = result
            embed.add_field(name=user_name, value=f'Level: {level} Points: {points}', inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BattlepassCog(bot))