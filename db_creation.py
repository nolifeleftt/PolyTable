import sqlite3

conn = sqlite3.connect('users.db')

cursor = conn.cursor()

cursor.execute('''CREATE TABLE users
                 (id INTEGER PRIMARY KEY,
                  username TEXT,
                  group_name TEXT,
                  group_id INTEGER)''')

conn.commit()