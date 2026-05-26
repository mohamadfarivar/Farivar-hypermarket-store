from db import get_db_connection


connection = get_db_connection()

cursor = connection.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS products (

    id SERIAL PRIMARY KEY,

    name TEXT NOT NULL,

    price INTEGER NOT NULL,

    image TEXT NOT NULL,

    description TEXT NOT NULL,

    category_id INTEGER,

    stock INTEGER DEFAULT 0

)

""")

connection.commit()

cursor.close()

connection.close()

print("Products table created successfully!")
