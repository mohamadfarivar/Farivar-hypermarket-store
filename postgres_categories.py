from db import get_db_connection


connection = get_db_connection()

cursor = connection.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS categories (

    id SERIAL PRIMARY KEY,

    name TEXT NOT NULL

)

""")

connection.commit()

cursor.close()

connection.close()

print("Categories table created successfully!")
