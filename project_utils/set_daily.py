import sqlite3
from datetime import datetime, timedelta


conn = sqlite3.connect('data/battlepass.db')
cursor = conn.cursor()

yesterday = datetime.now() - timedelta(days=1)
query = f'UPDATE battlepass SET daily_redemption = ?'
cursor.execute(query, yesterday)

conn.commit()
cursor.close()
conn.close()
