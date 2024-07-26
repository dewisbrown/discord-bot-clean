"""
Helper functions that don't fit into other categories.
"""

def decimal_to_hex(decimal: int) -> str:
    """
    Converts decimal number to hexadecimal string.
    """
    return hex(decimal).split('x')[-1]
