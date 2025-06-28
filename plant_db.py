import psycopg2 as pg2
from dotenv import load_dotenv
import os

# Load .env or .env.test based on ENV variable
env_file = ".env.test" if os.getenv("ENV") == "test" else ".env"
load_dotenv(".env.test", override=True) if os.getenv("ENV") == "test" else load_dotenv(override=True)

# Print to confirm which env file was loaded
print(f"🌍 Loaded environment file: {env_file}")

# Print important DB environment variables to verify
print(f"🧪 ENV = {os.getenv('ENV')}")
print(f"🌱 DB_NAME = {os.getenv('DB_NAME')}")
print(f"👤 DB_USER = {os.getenv('DB_USER')}")
print(f"🛡️ DB_HOST = {os.getenv('DB_HOST')}")

# 1. Connect to your PostgreSQL database
conn = pg2.connect(
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")          
)

# 2. Create a cursor object to execute SQL commands
cur = conn.cursor()


# 3. Execute a SQL query to create the table
'''cur.execute("""
    INSERT INTO plants (
        plant_name,
        plant_class,
        plant_date
    )
    VALUES (
        'Dandelion01',
        'Asteraceae',
        CURRENT_DATE
    );
""")'''

'''cur.execute("""
    CREATE TABLE plants (
        plant_id SERIAL PRIMARY KEY,
        plant_name TEXT UNIQUE NOT NULL,
        plant_class TEXT NOT NULL,
        plant_date DATE NOT NULL,
        plant_notes TEXT
    );
""")'''

cur.execute("ALTER TABLE plants RENAME COLUMN plant_name TO plant_name_en;")
cur.execute("ALTER TABLE plants RENAME COLUMN plant_class TO plant_class_en;")
cur.execute("ALTER TABLE plants ADD COLUMN plant_name_ja TEXT;")
cur.execute("ALTER TABLE plants ADD COLUMN plant_class_ja TEXT;")


"""cur.execute("CREATE DATABASE plant_db_test;")"""
'''cur.execute("TRUNCATE TABLE plants;")
cur.execute("DELETE FROM plants WHERE plant_name = 'Tulip';")'''
"""cur.execute("TRUNCATE TABLE plants RESTART IDENTITY;")"""
"""cur.execute("ALTER TABLE plants ALTER COLUMN plant_name SET NOT NULL;")
cur.execute("ALTER TABLE plants ALTER COLUMN plant_class SET NOT NULL;")
cur.execute("ALTER TABLE plants ALTER COLUMN plant_class SET NOT NULL;")""""""
cur.execute("ALTER TABLE plants ADD CONSTRAINT unique_plant_name UNIQUE (plant_name);")"""
"""cur.execute("DELETE FROM plants WHERE plant_id = 58")"""
cur.execute("SELECT * FROM plants")
rows = cur.fetchall()
for row in rows:
    print(row)


# 4. Commit changes to the database
conn.commit()



# (Optional) Verify table creation — not needed for CREATE TABLE
print("Successfully updated or queried!")

# 5. Always close the cursor and connection when done
cur.close()
conn.close()

