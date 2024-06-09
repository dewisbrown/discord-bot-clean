import sqlite3

# Connect to sqlite database (make new if doesn't exist)
conn = sqlite3.connect('data/battlepass.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()
while True:
    item_name = input('Item name (\'exit\' to stop): ')
    if item_name == 'exit':
        break
    value = int(input('Value: '))
    print('1. Legendary\n2. Very Rare\n3. Rare\n4. Uncommon\n5. Common')
    choice = input()
    if choice == '1':
        rarity = 'Legendary'
    elif choice == '2':
        rarity = 'Very Rare'
    elif choice == '3':
        rarity = 'Rare'
    elif choice == '4':
        rarity = 'Uncommon'
    elif choice == '5':
        rarity = 'Common'

    image_url = input('Image url: ')
    cursor.execute('''INSERT INTO shop (item_name, value, rarity, image_url)
                   VALUES (?, ?, ?, ?)''', (item_name, value, rarity, image_url,))

conn.commit()
conn.close()
