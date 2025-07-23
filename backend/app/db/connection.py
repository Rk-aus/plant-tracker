import os
import psycopg2 as pg2

def get_connection():
    """
    Establishes and returns a connection to the PostgreSQL database using environment variables.

    Returns:
        psycopg2.extensions.connection: A new database connection object.
    """
    return pg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )