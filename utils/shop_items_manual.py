import sqlite3

def import_items():
    with open('Shop.txt', 'r', encoding='utf-8') as file:
        # Connect to sqlite database (make new if doesn't exist)
        conn = sqlite3.connect('data/battlepass.db')

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        for line in file:
            split_line = line.split(',')
            item = split_line[0].strip()
            rarity = split_line[1].strip()
            query = 'INSERT INTO shop (item_name, rarity) VALUES (?, ?)'
            cursor.execute(query, (item, rarity))

        conn.commit()
        conn.close()

def show_items():
    # Connect to sqlite database (make new if doesn't exist)
    conn = sqlite3.connect('data/battlepass.db')

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    query = 'SELECT * FROM shop'
    cursor.execute(query)
    items = cursor.fetchall()

    for item in items:
        print(item)

show_items()