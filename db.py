import sqlite3
import psycopg2

from psycopg2.extras import RealDictCursor


def get_db_connection():

    connection = psycopg2.connect(

        host="localhost",

        database="farivar_store",

        user="postgres",

        password="Farivar1123@#",

        cursor_factory=RealDictCursor

    )

    return connection


def get_sqlite_connection():

    connection = sqlite3.connect("database.db")

    connection.row_factory = sqlite3.Row

    return connection
