import sqlite3
import os

from dotenv import load_dotenv

load_dotenv()
DB_FILE = os.getenv('ABS_DB_PATH')

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
