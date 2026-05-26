import sqlite3

from db import get_db_connection


sqlite_connection = sqlite3.connect("database.db")

sqlite_connection.row_factory = sqlite3.Row

sqlite_cursor = sqlite_connection.cursor()


postgres_connection = get_db_connection()

postgres_cursor = postgres_connection.cursor()


sqlite_cursor.execute("""

SELECT * FROM products

""")

products = sqlite_cursor.fetchall()


for product in products:

    postgres_cursor.execute("""

    INSERT INTO products (
        name,
        price,
        image,
        description,
        category_id,
        stock
    )

    VALUES (%s, %s, %s, %s, %s, %s)

    """, (

        product["name"],
        int(product["price"].replace("$", "")),
        product["image"],
        product["description"],
        product["category_id"],
        product["stock"]

    ))


postgres_connection.commit()

sqlite_cursor.close()

sqlite_connection.close()

postgres_cursor.close()

postgres_connection.close()

print("Products migrated successfully!")
