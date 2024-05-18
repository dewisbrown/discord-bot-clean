"""
Module for helper functions and constants.
Keeping inside cog directory for easier import.
"""
import datetime


def points(level: int) -> int:
    """
    Points awarded to user for battlepass. Double points
    if redeemed between 18:00 and 22:00 CST.
    """
    BASE_POINTS = 15
    level_points = (level // 10) * 5
    total_points = BASE_POINTS + level_points

    now = datetime.datetime.now()
    start = datetime.datetime(now.year, now.month, now.day, 18, 0, 0)
    end = datetime.datetime(now.year, now.month, now.day, 22, 0, 0)

    double_xp = start <= now <= end

    if double_xp:
        return total_points * 2
    return total_points


def decimal_to_hex(decimal: int) -> str:
    """
    Converts decimal number to hexadecimal string.
    """
    return hex(decimal).split('x')[-1]


def points_to_level_up(level: int) -> int:
    """
    Calculates points required to increase level
    based on current level number.

    1: 100, 2:100, 3:120, 4:130...
    """
    return 10 * level + 90


def command_info(command: str) -> dict | None:
    """
    Grabs info for moderation.help command embeds.
    """
    _help = {
        'description': 'Displays information for bot commands.',
        'syntax': '`$help`\n`$help <command>`',
        'example': '`$help battlepass`',
    }
    battlepass = {
        'description': 'Displays level and points for user.',
        'syntax': '`$battlepass`',
        'example': '`$battlepass`',
    }
    _points = {
        'description': 'Gain points every 15 minutes.',
        'syntax': '`$points`',
        'example': '`$points`',
    }
    register = {
        'description': 'Register for battlepass.',
        'syntax': '`$register`',
        'example': '`$register`',
    }
    tierup = {
        'description': 'Spend points to increase battlepass level.',
        'syntax': '`$tierup`',
        'example': '`$tierup`',
    }
    top5 = {
        'description': 'Displays top 5 battlepass members.',
        'syntax': '`$top5`',
        'example': '`$top5`',
    }
    buy = {
        'description': 'Purchase item from item shop.',
        'syntax': '`$buy <item_name>`',
        'example': '`$buy Winton Plush`',
    }
    inventory = {
        'description': 'Displays user inventory.',
        'syntax': '`$inventory`',
        'example': '`$inventory`',
    }
    shop = {
        'description': 'Displays shop items and values, refreshes every thirty minutes.',
        'syntax': '`$shop`',
        'example': '`$shop`',
    }
    submit_item = {
        'description': 'Submit item shop ideas.\nValid rarities: Legendary, Very Rare, Rare, Uncommon, Common',
        'syntax': '`$submit_item <item_name>, <rarity>`',
        'example': '`$submit_item Winton Plush, Legendary`',
    }
    play = {
        'description': 'Plays YouTube video audio in voice channel. Option to provide YouTube link, Spotify link, or search terms.',
        'syntax': '`$play <youtube_url>`\n`$play <search_terms>`\n`$play <spotify_link>`',
        'example': '`$play https://www.youtube.com/watch?v=L_jWHffIx5E`\n`$play All Star Smash Mouth`',
    }
    queue = {
        'description': 'Displays the music queue.',
        'syntax': '`$queue`',
        'example': '`$queue`',
    }
    stop = {
        'description': 'Stops the music player and the bot exits the voice channel.',
        'syntax': '`$stop`',
        'example': '`$stop`',
    }
    game = {
        'description': 'Bot selects random game title out of provided game titles.',
        'syntax': '`$game <game_1>, <game_2>, ..., <game_n>`',
        'example': '`$game overwatch, rocket league, dead by daylight, fall guys`',
    }
    discordstatus = {
        'description': 'Checks discord status for US East and US Central servers.',
        'syntax': '`$discordstatus`',
        'example': '`$discordstatus`',
    }
    age = {
        'description': 'Displays user time since joining server.',
        'syntax': '`$age`',
        'example': '`$age`',
    }
    updates = {
        'description': 'Displays recent changes made to GummyBot.',
        'syntax': '`$updates`',
        'example': '`$updates`',
    }
    ufc = {
        'description': 'Displays next four UFC event dates, times, and titles.',
        'syntax': '`$ufc`',
        'example': '`$ufc`',
    }
    elijah = {
        'description': 'Displays welcome back message for Elijah.',
        'syntax': '`$elijah`',
        'example': '`$elijah`',
    }
    mark = {
        'description': 'Displays days since Mark left.',
        'syntax': '`$mark`',
        'example': '`$mark`',
    }

    commands = {
        'help': _help,
        'battlepass': battlepass,
        'points': _points,
        'register': register,
        'tierup': tierup,
        'top5': top5,
        'buy': buy,
        'inventory': inventory,
        'shop': shop,
        'submit_item': submit_item,
        'play': play,
        'queue': queue,
        'stop': stop,
        'game': game,
        'discordstatus': discordstatus,
        'age': age,
        'updates': updates,
        'ufc': ufc,
        'elijah': elijah,
        'mark': mark
    }

    if command in commands.keys():
        return commands[command]
    return None
