import logging
import datetime
import discord
import pytz
from discord.ext import commands, tasks
import db_interface as db

shop = []
refresh_time = datetime.datetime.now()

class ShopCog(commands.Cog):
    '''Commands for viewing item shop, buying, and viewing own inventory.'''
    def __init__(self, bot):
        self.bot = bot
        refresh_shop.start()


    @commands.Cog.listener()
    async def on_ready(self):
        '''Print statment to ensure loads properly.'''
        logging.info('Shop Cog loaded.')


    @commands.command()
    async def shop(self, ctx):
        '''Prints the shop items and values.'''
        embed = discord.Embed(title='Item Shop', description=f'Refreshes at {refresh_time.strftime("%H:%M %Z")}', timestamp=datetime.datetime.now())
        embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)
        embed.set_thumbnail(url='https://wallpapercave.com/wp/wp7879327.jpg')

        for item in shop:
            item_name, item_value, item_rarity = item
            embed.add_field(name=item_name, value=f'Points: {item_value} - Rarity: {item_rarity}', inline=False)

        await ctx.send(embed=embed)


    @commands.command()
    async def inventory(self, ctx):
        '''Lists the user's inventory.'''
        user_id = ctx.author.id
        items = db.get_inventory(user_id=user_id)

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
        '''Purchase item from shop.'''
        user_id = ctx.author.id

        # Check if user is registered for battlepass
        user = db.get_user_id(user_id=user_id)
        if user is None:
            await ctx.send('''Register for the battlepass to earn 
                           points and purchase items by using the 
                           `$register` command.''')
            return

        # Check if item is currently in shop
        if item_name not in [item[0] for item in shop]:
            await ctx.send(f'{item_name} is not in the shop. Use `$shop` to see items in the shop.')
            return

        # Check if user already owns the item
        owned_item = db.get_owned_item(user_id=user_id, item_name=item_name)
        if owned_item:
            await ctx.send('You already own this item.')
            return

        # Check if user has enough points to purchase item
        points = int(db.get_points(user_id=user_id))
        for item in shop:
            if item_name == item[0]:
                item_value = item[1]
                item_rarity = item[2]
                break

        embed = discord.Embed(title='Item Purchase', timestamp=datetime.datetime.now())
        embed.set_author(name=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar)

        if points >= item_value:
            # Deduct item value from user points
            db.set_points(user_id=user_id, points=points - item_value)

            # Add item to user inventory
            db.add_to_inventory(
                user_id=user_id,
                item_name=item_name,
                item_value=item_value,
                item_rarity=item_rarity,
                purchase_date=datetime.datetime.now())

            embed.add_field(name=f'{item_name} has been added to your inventory', value='View your inventory by using `$inventory`.', inline=False)
            embed.add_field(name='', value=f'Points after purchase: {points - item_value}', inline=False)
        else:
            embed.add_field(name=f'You do not have enough points to purchase {item_name}.', value='', inline=False)
            embed.add_field(name='', value=f'Your points: {points}', inline=False)
            embed.add_field(name='', value=f'{item_name}: {item_value} points.', inline=False)
        await ctx.send(embed=embed)


@tasks.loop(minutes=30)
async def refresh_shop():
    '''Updates shop with five new items every thirty minutes.'''
    global shop
    shop = db.get_shop_items()

    current_time = datetime.datetime.now(pytz.timezone('US/Central'))
    set_shop_refresh_time(current_time + datetime.timedelta(minutes=30))


def set_shop_refresh_time(timestamp):
    '''Updates shop refresh time whenever refresh_shop task runs.'''
    global refresh_time
    refresh_time = timestamp


async def setup(bot):
    '''Runs when bot.load_extension() is called.'''
    await bot.add_cog(ShopCog(bot))
