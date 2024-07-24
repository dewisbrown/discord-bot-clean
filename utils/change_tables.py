import sqlite3
import os
import datetime


rel_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'battlepass.db')
DB_FILE = os.path.abspath(rel_path)

def add_column_to_table(table_name: str, col_name: str, col_type: str) -> None:
    """
    Add a column to an existing table.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}'
    cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()

def print_table_columns(table_name: str) -> list:
    """
    Prints table columns to console.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = f'PRAGMA table_info({table_name})'
    cursor.execute(query)

    col_info = cursor.fetchall()
    for col in col_info:
        print(col)

    cursor.close()
    conn.close()

def set_daily_redemption() -> None:
    """
    Sets all users' 'daily_redemption' to 1 day ago.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    query = 'UPDATE battlepass SET daily_redemption = ?'
    cursor.execute(query, (yesterday,))

    conn.commit()
    cursor.close()
    conn.close()

def update_user_points(points: int, user_name: str) -> None:
    """
    Manually set points for a user.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = 'UPDATE battlepass SET points = ? WHERE user_name = ?'
    cursor.execute(query, (points, user_name))

    conn.commit()
    conn.close()
