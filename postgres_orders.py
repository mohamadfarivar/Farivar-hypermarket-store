from db import get_db_connection


connection = get_db_connection()

cursor = connection.cursor()


cursor.execute("""

CREATE TABLE IF NOT EXISTS orders (

    id SERIAL PRIMARY KEY,

    user_id INTEGER,

    customer_name TEXT NOT NULL,

    phone TEXT NOT NULL,

    address TEXT NOT NULL,

    total_price INTEGER NOT NULL,

    status TEXT DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)

""")


cursor.execute("""

CREATE TABLE IF NOT EXISTS order_items (

    id SERIAL PRIMARY KEY,

    order_id INTEGER NOT NULL,

    product_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    FOREIGN KEY(order_id)
    REFERENCES orders(id),

    FOREIGN KEY(product_id)
    REFERENCES products(id)

)

""")


connection.commit()

cursor.close()

connection.close()

print("Orders tables created successfully!")
