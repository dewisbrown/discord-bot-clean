"""
Using to minimize re-written code in cog files. 
Provides a way to input and retreive data from database.
"""
import sqlite3
import os

from dotenv import load_dotenv


load_dotenv()
DB_FILE = os.getenv('DB_PATH')

def get_user_id(**kwargs):
    """
    Retrieves user id from battlepass table.
    Used to check if user is enrolled already.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    conditions = []
    values = []

    # build WHERE clause based on kwargs
    for key, value in kwargs.items():
        conditions.append(f'{key} = ?')
        values.append(value)
    where_clause = ' AND '.join(conditions)

    # build query with where clause (if kwargs were supplied)
    query = 'SELECT user_id FROM battlepass'
    if conditions:
        query += f' WHERE {where_clause}'

    # Execute query with values from kwargs
    cursor.execute(query, tuple(values))

    return cursor.fetchone()

def create_user(user_id: int, redemption_time, user_name: str, guild_id: int, daily_redemption):
    """
    Enters user into battlepass table.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO battlepass (
                   user_id, guild_id, points, redemption_time, 
                   level, user_name, daily_redemption) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (user_id, guild_id, 120, redemption_time, 1, user_name, daily_redemption))
    conn.commit()

def retrieve_points(user_id: int):
    """
    Retrieves user points from battlepass table.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check the last awarded timestamp for the user
    cursor.execute('SELECT points FROM battlepass WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    return result[0]

def retrieve_redemption_time(user_id: int):
    """
    Retrieves timestamp of last point redemption for a user.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check the last awarded timestamp for the user
    cursor.execute('SELECT redemption_time FROM battlepass WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

def retrieve_daily_redemption_time(user_id: int):
    """
    Retrieves timestamp of last daily point redemption for a user.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check the last awarded timestamp for the user
    cursor.execute('SELECT daily_redemption FROM battlepass WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

def update_redemption_time(user_id: int, current_time):
    """
    Updates timestamp for most recent point redemption for a user.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check the last awarded timestamp for the user
    cursor.execute('''UPDATE battlepass SET redemption_time = ?
                   WHERE user_id = ?''', (current_time, user_id))
    conn.commit()
    conn.close()

def update_daily_redemption_time(user_id: int, current_time):
    """
    Updates timestamp for most recent daily point redemption for a user.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check the last awarded timestamp for the user
    cursor.execute('''UPDATE battlepass SET daily_redemption = ?
                   WHERE user_id = ?''', (current_time, user_id))
    conn.commit()
    conn.close()

def update_points(user_id: int, points: int) -> None:
    """
    Updates user points.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check the last awarded timestamp for the user
    cursor.execute('UPDATE battlepass SET points = ? WHERE user_id = ?', (points, user_id))
    conn.commit()
    conn.close()

def retrieve_level(user_id: int):
    """
    Retrieves user level.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT level FROM battlepass WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

def update_level(user_id: int, level: int):
    """
    Update user level.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('UPDATE battlepass SET level = ? WHERE user_id = ?', (level, user_id,))
    conn.commit()
    conn.close()

def retrieve_inventory(user_id: int):
    """
    Retrieves user inventory.
    Format of each returned record: (item_name, value, rarity).
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Return user inventory list
    cursor.execute('''SELECT item_name, value, rarity
                        FROM inventory
                        WHERE user_id = ?''', (user_id,))
    # for item in items -> item_name = item[0], value = item[1], rarity = item[2]
    return cursor.fetchall()

def update_inventory(user_id: int,
                     guild_id: int,
                     item_name: str,
                     value: int,
                     rarity: str,
                     purchase_date):
    """
    Creates inventory record.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Extract data from item_info and add to inventory
    cursor.execute('''INSERT INTO inventory
                   (user_id, guild_id, item_name, value, rarity, purchase_date) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                   (user_id, guild_id, item_name, value, rarity, purchase_date))
    conn.commit()
    conn.close()

def retrieve_top_five(guild_id: int):
    """
    Retrieve list of five highest point users.
    Format of each record returned: (user_name, level, points).
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Checks top 5 users in given guild
    query = 'SELECT user_name, level, points FROM battlepass WHERE guild_id = ? ORDER BY level DESC, points DESC LIMIT 5'
    cursor.execute(query, (guild_id,))
    return cursor.fetchall()

def retrieve_shop_items() -> list:
    """
    Retrieves ten items at random from shop table. Format 
    of each record returned: (item_name, rarity, img_url).
    """
    # Can be rarity counts can be changed at any time
    rarity_counts = {
        'Legendary': 1,
        'Exotic': 1,
        'Very Rare': 1,
        'Rare': 2,
        'Uncommon': 2,
        'Common': 3
    }

    # Connect to sqlite database (make new if doesn't exist)
    conn = sqlite3.connect(DB_FILE)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    selected_items = []

    for rarity, count in rarity_counts.items():
        query = 'SELECT * FROM shop WHERE rarity = ? ORDER BY RANDOM() LIMIT ?'
        cursor.execute(query, (rarity, count))
        selected_items.extend(cursor.fetchall())

    conn.close()
    return selected_items

def retrieve_owned_item(user_id: int, item_name: str):
    """
    Retrieves item from user inventory. Returns None if user does not have item.
    """
    # Connect to sqlite database (make new if doesn't exist)
    conn = sqlite3.connect(DB_FILE)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    query = 'SELECT item_name FROM inventory WHERE user_id = ? AND item_name = ?'
    cursor.execute(query, (user_id, item_name))

    return cursor.fetchone()

def create_shop_item(item_name: str, rarity: str, img_url: str):
    """
    Enter shop item info to db table.
    """
    # Connect to sqlite database (make new if doesn't exist)
    conn = sqlite3.connect(DB_FILE)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    query = '''INSERT INTO shop (item_name, rarity, img_url) 
                VALUES (?, ?, ?)'''
    cursor.execute(query, (item_name, rarity, img_url))
    conn.commit()
    conn.close()

def create_shop_submission(
        user_id: int,
        user_name: str,
        submit_time,
        item_name: str,
        rarity: str) -> None:
    """
    Creates shop item in item_submissions table.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = '''INSERT INTO shop_submissions
            (user_id, user_name, submit_time, item_name, rarity)
            VALUES (?, ?, ?, ?, ?)'''

    cursor.execute(query,(user_id, user_name, submit_time, item_name, rarity))
    conn.commit()
    conn.close()

def retrieve_shop_submission(item_name: str):
    """
    Retrieves shop submission by name.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = 'SELECT * FROM shop_submissions WHERE item_name = ?'
    cursor.execute(query, (item_name))
    return cursor.fetchone()

def retrieve_shop_submissions():
    """
    Retreives all shop submissions. Format of each returned record:
    (item_id, user_id, user_name, submit_time, item_name, rarity).
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shop_submissions')
    return cursor.fetchall()

# Currently not in use, not sure if needed or wanted.
def create_command_request(user_id: int, guild_id: int, command: str, cog: str) -> None:
    """
    Creates record in command_request table.
    """
    # Connect to sqlite database (make new if doesn't exist)
    conn = sqlite3.connect(DB_FILE)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    query = '''INSERT INTO command_requests
            (user_id, guild_id, command, cog) 
            VALUES (?, ?, ?, ?)'''
    cursor.execute(query, (user_id, guild_id, command, cog))
    conn.commit()
    conn.close()
