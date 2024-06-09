import sqlite3
import os


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

def remove_column_from_table(table_name: str, col_name: str) -> None:
    """
    Removes a column from an existing table.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # TODO: implement logic for removing column
    query = f''
    cursor.execute(query)

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
