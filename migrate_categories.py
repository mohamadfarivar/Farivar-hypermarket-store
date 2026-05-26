import sqlite3

from db import get_db_connection


sqlite_connection = sqlite3.connect("database.db")

sqlite_connection.row_factory = sqlite3.Row

sqlite_cursor = sqlite_connection.cursor()


postgres_connection = get_db_connection()

postgres_cursor = postgres_connection.cursor()


sqlite_cursor.execute("""

SELECT * FROM categories

""")

categories = sqlite_cursor.fetchall()


for category in categories:

    postgres_cursor.execute("""

    INSERT INTO categories (
        name
    )

    VALUES (%s)

    """, (
        category["name"],
    ))


postgres_connection.commit()

sqlite_cursor.close()

sqlite_connection.close()

postgres_cursor.close()

postgres_connection.close()

print("Categories migrated successfully!")
