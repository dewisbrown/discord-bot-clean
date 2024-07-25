import os

from .change_tables import add_column_to_table, print_table_columns
from .modify_db import set_daily_redemption, update_user_points, create_battlepass_entry
from .misc import decimal_to_hex
from .commands import calculate_points, points_to_level_up, get_command_help
from .db_interface import *


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