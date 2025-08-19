import os
from psycopg2 import pool

_connection_pool = None

def init_connection_pool(minconn: int = 1, maxconn: int = 10):
    """
    Initialize a PostgreSQL connection pool.

    Args:
        minconn (int): Minimum number of connections to maintain.
        maxconn (int): Maximum number of connections allowed.
    """
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = pool.SimpleConnectionPool(
            minconn,
            maxconn,
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

def get_connection():
    """
    Borrow a connection from the pool.
    
    Returns:
        psycopg2.extensions.connection: A PostgreSQL connection object.
    """
    if _connection_pool is None:
        raise RuntimeError("Connection pool is not initialized. Call init_connection_pool first.")
    return _connection_pool.getconn()

def release_connection(conn):
    """
    Return a connection back to the pool.
    
    Args:
        conn (psycopg2.extensions.connection): Connection to release.
    """
    if _connection_pool is None:
        raise RuntimeError("Connection pool is not initialized.")
    _connection_pool.putconn(conn)

def close_all_connections():
    """
    Close all connections in the pool.
    """
    if _connection_pool:
        _connection_pool.closeall()