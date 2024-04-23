"""
Using to minimize re-written code in cog files. 
Provides a way to input and retreive data from database.
"""

import sqlite3
import os
from dotenv import load_dotenv


# Load db file path from .env file
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'data/battlepass.db')


def get_user_id(user_id):
    """
    Retrieves user id from battlepass table.
    Used to check if user is enrolled already.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if the user is already registered
    cursor.execute('SELECT user_id FROM battlepass WHERE user_id = ?', (user_id,))
    return cursor.fetchone()


def create_user(user_id: int, last_awarded_at, user_name: str, guild_id: int):
    """
    Enters user into battlepass table.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO battlepass (
                   user_id, guild_id, points, last_awarded_at, 
                   level, user_name) VALUES (?, ?, ?, ?, ?, ?)''', 
                   (user_id, guild_id, 100, last_awarded_at, 1, user_name))
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


def retrieve_last_awarded_at(user_id: int):
    """
    Retrieves timestamp of last point redemeption for a user.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check the last awarded timestamp for the user
    cursor.execute('SELECT last_awarded_at FROM battlepass WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None


def update_last_awarded_at(user_id: int, current_time):
    """
    Updates timestamp for most recent point redemption for a user.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check the last awarded timestamp for the user
    cursor.execute('''UPDATE battlepass SET last_awarded_at = ?
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
                     item_name: str, 
                     item_value: int, 
                     item_rarity: str, 
                     purchase_date):
    """
    Creates inventory record.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Extract data from item_info and add to inventory
    cursor.execute('''INSERT INTO inventory
                   (user_id, item_name, value, rarity, purchase_date) 
                   VALUES (?, ?, ?, ?, ?)''',
                   (user_id, item_name, item_value, item_rarity, purchase_date))
    conn.commit()
    conn.close()


def retrieve_top_five():
    """
    Retrieve list of five highest point users.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Checks top 5 users
    cursor.execute('''SELECT user_name, level, points FROM points
                   ORDER BY level DESC, points DESC LIMIT 5''')
    return cursor.fetchall()


def retrieve_shop_items():
    """
    Retrieves ten items at random from shop table.
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
