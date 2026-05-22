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

    stock INTEGER DEFAULT 0,

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


cursor.execute("""

CREATE TABLE IF NOT EXISTS orders (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    customer_name TEXT NOT NULL,

    phone TEXT NOT NULL,

    address TEXT NOT NULL,

    total_price INTEGER NOT NULL,

    status TEXT DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
    REFERENCES users(id)

)

""")


cursor.execute("""

CREATE TABLE IF NOT EXISTS order_items (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    order_id INTEGER NOT NULL,

    product_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    FOREIGN KEY(order_id)
    REFERENCES orders(id),

    FOREIGN KEY(product_id)
    REFERENCES products(id)

)

""")



cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL

)

""")



cursor.execute("""

CREATE TABLE IF NOT EXISTS reviews (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    product_id INTEGER NOT NULL,

    rating INTEGER NOT NULL,

    comment TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
    REFERENCES users(id),

    FOREIGN KEY(product_id)
    REFERENCES products(id)

)

""")



connection.commit()

connection.close()

print("Database created successfully.")