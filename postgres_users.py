from db import get_db_connection


connection = get_db_connection()

cursor = connection.cursor()

cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id SERIAL PRIMARY KEY,

    username TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL

)

""")

connection.commit()

cursor.close()

connection.close()

print("Users table created successfully!")
