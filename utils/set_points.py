import sqlite3

# Change to working db file path as needed
DB_FILE = 'data/battlepass.db'

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Change to table you want to update
table = 'battlepass'
query = f'UPDATE {table} SET points = ? WHERE user_name = ?'

# Adjust points and username before running
points = 0
user_name = ''
cursor.execute(query, (points, user_name))

conn.commit()
conn.close()
