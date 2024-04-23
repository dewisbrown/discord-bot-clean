"""
Module for helper functions and constants.
Keeping inside cog directory for easier import.
"""
def points(double_xp: bool) -> int:
    """
    Points awarded to user for battlepass. False arg
    returns 15 points, while True returns 30.
    """
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