"""
Module for helper functions and constants.
Keeping inside cog directory for easier import.
"""
import datetime


def points() -> int:
    """
    Points awarded to user for battlepass. Double points
    if redeemed between 18:00 and 22:00 CST.
    """
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, now.month, now.day, 18, 0, 0)
    end = datetime.datetime(now.year, now.month, now.day, 22, 0, 0)

    double_xp = start <= now <= end

    if double_xp:
        return 30
    else:
        return 15


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