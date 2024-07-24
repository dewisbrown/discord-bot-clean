import os

from .change_tables import add_column_to_table, print_table_columns
from .modify_db import set_daily_redemption, update_user_points


rel_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'battlepass.db')
DB_FILE = os.path.abspath(rel_path)

__version__ = '0.0.1'
__author__ = 'dewisbrown'
__all__ = [
    'add_column_to_table',
    'print_table_columns',
    'set_daily_redemption',
    'update_user_points',
]