import sqlite3

conn = sqlite3.connect('data/battlepass.db')
cursor = conn.cursor()

# input variables in execute function
cursor.execute('INSERT INTO battlepass (user_id, points, last_awarded_at, level, user_name) VALUES (?, ?, ?, ?, ?)', ())
conn.commit()

conn.close()