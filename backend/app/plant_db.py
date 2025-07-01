import psycopg2 as pg2
from dotenv import load_dotenv
import os

env_file = ".env.test" if os.getenv("ENV") == "test" else ".env"
(
    load_dotenv(".env.test", override=True)
    if os.getenv("ENV") == "test"
    else load_dotenv(override=True)
)

print(f"🌍 Loaded environment file: {env_file}")
print(f"🧪 ENV = {os.getenv('ENV')}")
print(f"🌱 DB_NAME = {os.getenv('DB_NAME')}")
print(f"👤 DB_USER = {os.getenv('DB_USER')}")
print(f"🛡️ DB_HOST = {os.getenv('DB_HOST')}")

conn = pg2.connect(
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
)

cur = conn.cursor()

cur.execute("SELECT * FROM plants")
rows = cur.fetchall()
for row in rows:
    print(row)

conn.commit()

print("Successfully updated or queried!")

cur.close()
conn.close()
