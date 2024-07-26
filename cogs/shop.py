import logging
import datetime
import math
import random

import discord
import pytz
from discord.ext import commands, tasks
import discord.ext

import utils

shop = {}
refresh_time = datetime.datetime.now()

class ShopCog(commands.Cog):
    """
    Commands for viewing item shop, buying, and viewing own inventory.
    """
    def __init__(self, bot):
        self.bot = bot
        refresh_shop.start()


    @commands.Cog.listener()
    async def on_ready(self):
        """
        Print statment to ensure loads properly.
        """
        logging.info('Shop Cog loaded.')


    @commands.command()
    async def shop(self, ctx):
        """
        Prints the shop items and values.
        """
        embed = discord.Embed(title='Item Shop', description=f'Refreshes at {refresh_time.strftime("%H:%M %Z")}', timestamp=datetime.datetime.now())
        embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)
        embed.set_thumbnail(url='https://wallpapercave.com/wp/wp7879327.jpg')

        for k, v in shop.items():
            item_name = k
            rarity, value = v
            embed.add_field(name=item_name, value=f'Points: {value} - Rarity: {rarity}', inline=False)

        await ctx.send(embed=embed)


    @commands.command()
    async def inventory(self, ctx, user_name=None):
        """
        Lists the user's inventory.
        """
        logging.info('Inventory command submitted by [%s:%s]', ctx.author, ctx.author.id)
        if user_name:
            # Check if user is in same guild as ctx.author
            user_id = utils.get_user_id(user_name=user_name, guild_id=ctx.author.guild.id)
            if user_id:
                user_id = int(user_id[0])
                items = utils.retrieve_inventory(user_id=user_id)
                if items:
                    embed = discord.Embed(title='Inventory', timestamp=datetime.datetime.now())
                    embed.set_author(name=user_name)
                    embed.set_thumbnail(url='https://www.kindpng.com/picc/m/172-1721685_image-png-international-file-dora-the-explorer-backpack.png')
                    for item in items:
                        embed.add_field(name=item[0], value=f'Value: {item[1]} - Rarity: {item[2]}', inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f'{user_name} has an empty inventory.')
            else:
                await ctx.send(f'The user [{user_name}] is not in this guild or has not registered for the battlepass.')
        else:
            user_id = ctx.author.id
            items = utils.retrieve_inventory(user_id=user_id)

            if items:
                embed = discord.Embed(title='Inventory', timestamp=datetime.datetime.now())
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
                embed.set_thumbnail(url='https://www.kindpng.com/picc/m/172-1721685_image-png-international-file-dora-the-explorer-backpack.png')
                for item in items:
                    embed.add_field(name=item[0], value=f'Value: {item[1]} - Rarity: {item[2]}', inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send('Your inventory is empty.')


    @commands.command()
    async def buy(self, ctx, *, item_name):
        """
        Purchase item from shop.
        """
        user_id = ctx.author.id
        guild_id = ctx.author.guild.id

        # Check if user is registered for battlepass
        user = utils.get_user_id(user_id=user_id)
        if user is None:
            await ctx.send('''Register for the battlepass to earn 
                           points and purchase items by using the 
                           `$register` command.''')
            return

        # Check if item is currently in shop
        item = shop.get(item_name)
        if item:
            # Check if user already owns the item
            owned_item = utils.retrieve_owned_item(user_id=user_id, item_name=item_name)
            if owned_item:
                await ctx.send('You already own this item.')
                return

            # Check if user has enough points to purchase item
            points = int(utils.retrieve_points(user_id=user_id))
            rarity = item[0]
            value = item[1]

            embed = discord.Embed(title='Item Purchase', timestamp=datetime.datetime.now())
            embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)

            if points >= value:
                # Deduct item value from user points
                utils.update_points(user_id=user_id, points=points - value)

                # Add item to user inventory
                utils.update_inventory(
                    user_id=user_id,
                    guild_id=guild_id,
                    item_name=item_name,
                    value=value,
                    rarity=rarity,
                    purchase_date=datetime.datetime.now()
                    )

                embed.add_field(name=f'{item_name} has been added to your inventory', value='View your inventory by using `$inventory`.', inline=False)
                embed.add_field(name='', value=f'Points after purchase: {points - value}', inline=False)
            else:
                embed.add_field(name=f'You do not have enough points to purchase {item_name}.', value='', inline=False)
                embed.add_field(name='', value=f'Your points: {points}', inline=False)
                embed.add_field(name='', value=f'{item_name}: {value} points.', inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'{item_name} is not in the shop. Use `$shop` to see items in the shop.')
            return


    @commands.command()
    async def submit_item(self, ctx, *, args):
        """
        Allows item submissions for item shop.
        """
        logging.info('Submit Item command submitted by [%s]', ctx.author.name)

        user_id = ctx.author.id
        user_name = ctx.author.name
        guild_id = ctx.author.guild.id
        guild_name = ctx.author.guild.name

        split_args: list[str] = args.split(',')
        if len(split_args) != 2:
            await ctx.send('Use `$help submit_item` for more information.')
        else:
            item_name = split_args[0].strip()
            rarity = split_args[1].strip()

            # Verify all args are valid
            if len(item_name) == 0:
                await ctx.send('Item name was blank.')
                return

            rarities = [
                'Legendary',
                'Very Rare',
                'Rare',
                'Uncommon',
                'Common'
            ]

            if rarity not in rarities:
                await ctx.send('Invalid rarity submitted. Use `$help submit_item` for more information.')
                return

            # If all args are valid, add to shop_submission table
            utils.create_shop_submission(
                user_id=user_id,
                user_name=user_name,
                submit_time=datetime.datetime.now(),
                item_name=item_name,
                rarity=rarity
            )

            embed = discord.Embed(
                title='Item Shop Submission',
                description='You have successfully submitted an item.',
                timestamp=datetime.datetime.now()
                )
            embed.add_field(name=item_name, value=f'Rarity: {rarity}', inline=False)
            await ctx.send(embed=embed)


    @commands.command()
    async def submissions(self, ctx):
        """
        Command to view item submissions.
        """
        logging.info('Submissions command submitted by [%s]', ctx.author.name)
        user_id = ctx.author.id
        user_name = ctx.author.name
        guild_id = ctx.author.guild.id
        guild_name = ctx.author.guild.name

        embed = discord.Embed(title='Item Submissions', timestamp=datetime.datetime.now())
        # embed.set_thumbnail(url='')

        items = utils.retrieve_shop_submissions()
        for item in items:
            embed.add_field(name=f'{item[5]}: {item[4]}', value=f'Submitted by: {item[2]}', inline=False)

        await ctx.send(embed=embed)


@tasks.loop(minutes=30)
async def refresh_shop():
    """
    Updates shop with ten new items every thirty minutes.
    """
    global shop
    shop.clear()

    shop_items = utils.retrieve_shop_items()
    for item in shop_items:
        item_name = item[0]
        rarity = item[1]
        value = calculate_value(rarity)
        shop[item_name] = [rarity, value]

    current_time = datetime.datetime.now(pytz.timezone('US/Central'))
    set_shop_refresh_time(current_time + datetime.timedelta(minutes=30))


def set_shop_refresh_time(timestamp):
    """
    Updates shop refresh time whenever refresh_shop task runs.
    """
    global refresh_time
    refresh_time = timestamp


def calculate_value(rarity: str) -> int:
    """
    Uses defined ranges for rarities to choose value at random.
    There is a higher chance to return the upper range of the rarity value.
    """
    rarity_price_ranges = {
        'Common': [50, 100, 200],
        'Uncommon': [200, 300, 500],
        'Rare': [500, 600, 750],
        'Very Rare': [750, 1000, 1500],
        'Legendary': [1500, 2000, 3000]
    }

    if random.randrange(0, 9) < 3:
        price = random.randrange(
                    rarity_price_ranges[rarity][0],
                    rarity_price_ranges[rarity][1]
                )
    else:
        price = random.randrange(
                    rarity_price_ranges[rarity][1],
                    rarity_price_ranges[rarity][2]
                )

    return math.ceil(price / 10.0) * 10


async def setup(bot):
    """
    Runs when bot.load_extension() is called. Adds shop cog to bot.
    """
    await bot.add_cog(ShopCog(bot))
