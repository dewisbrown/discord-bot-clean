import sqlite3

# Connect to sqlite database (make new if doesn't exist)
conn = sqlite3.connect('data/battlepass.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table to store member points
cursor.execute('''CREATE TABLE IF NOT EXISTS battlepass (
                    user_id INTEGER PRIMARY KEY,
                    guild_id INTEGER,
                    points INTEGER DEFAULT 20,
                    redemption_time TIMESTAMP,
                    level INTEGER DEFAULT 1,
                    user_name TEXT
                )''')
conn.commit()

# Create a table to store user inventory
cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    user_id INTEGER,
                    guild_id INTEGER,
                    item_name TEXT,
                    value INTEGER,
                    rarity TEXT,
                    img_url TEXT,
                    purchase_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES battlepass (user_id)
                )''')
conn.commit()

# Create a table to store shop items
cursor.execute('''CREATE TABLE IF NOT EXISTS shop (
                    item_name TEXT,
                    rarity TEXT,
                    img_url TEXT
                )''')
conn.commit()

# Create a table to store shop items
cursor.execute('''CREATE TABLE IF NOT EXISTS shop_submissions (
                    item_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    user_name TEXT,
                    submit_time TIMESTAMP,
                    item_name TEXT,
                    rarity TEXT
                )''')
conn.commit()

# Create a table to store bot command requests
cursor.execute('''CREATE TABLE IF NOT EXISTS command_requests (
                    user_id INTEGER,
                    guild_id INTEGER,
                    command TEXT,
                    cog TEXT,
                    command_time TIMESTAMP
               )''')
conn.commit()

# Close the connection
conn.close()
