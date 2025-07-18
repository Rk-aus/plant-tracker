import os
import psycopg2 as pg2
import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def clear_test_db():
    load_dotenv(dotenv_path="backend/.env.test", override=True)

    conn = pg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

    with conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE plants RESTART IDENTITY CASCADE;")

    conn.close()
