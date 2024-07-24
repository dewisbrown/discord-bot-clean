import sqlite3
import datetime

from . import DB_FILE


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
