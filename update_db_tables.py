import sqlite3


conn = sqlite3.connect('data/test.db')
cursor = conn.cursor()
try:
    cursor.execute('ALTER TABLE shop DROP COLUMN value')
    cursor.execute('ALTER TABLE shop RENAME COLUMN image_url TO img_url')
    cursor.execute('ALTER TABLE inventory ADD COLUMN img_url TEXT')
    conn.commit()
except sqlite3.Error as e:
    print('Error: ', e)
