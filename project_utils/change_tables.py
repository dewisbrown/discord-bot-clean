import sqlite3
import os


DB_FILE = os.path.join('..', 'data', 'battlepass.db')

def add_column_to_table(table_name: str, col_name: str) -> None:
    """
    Add a column to an existing table.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = ''
    cursor.execute(query, (table_name, col_name))

    conn.commit()
    conn.close()

def remove_column_from_table(table_name: str, col_name: str) -> None:
    """
    Removes a column from an existing table.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = ''
    cursor.execute(query, (table_name, col_name))

    conn.commit()
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
