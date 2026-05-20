import sqlite3

connection = sqlite3.connect("database.db")

cursor = connection.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS products (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    price TEXT NOT NULL,

    image TEXT NOT NULL,

    description TEXT NOT NULL,

    category_id INTEGER,

    FOREIGN KEY (category_id)
    REFERENCES categories(id)

)

""")

cursor.execute("""

CREATE TABLE IF NOT EXISTS categories (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL

)

""")

connection.commit()

connection.close()

print("Database created successfully.")