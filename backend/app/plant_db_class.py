import psycopg2 as pg2
from dotenv import load_dotenv
import os
from datetime import date


class PlantDB:
    def __init__(self):
        (
            load_dotenv(".env.test", override=True)
            if os.getenv("ENV") == "test"
            else load_dotenv(override=True)
        )

        print("🧪 ENV =", os.getenv("ENV"))
        print("🌱 DB_NAME =", os.getenv("DB_NAME"))

        self.conn = pg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        self.cur = self.conn.cursor()

    def insert_plant(
        self,
        plant_name_en,
        plant_name_ja,
        plant_class_en,
        plant_class_ja,
        image_path,
        botanical_name,
        location,
        plant_date=None,
    ):
        if not isinstance(plant_name_en, str) or not plant_name_en.strip():
            raise ValueError("English plant name must be a non-empty string.")
        if not isinstance(plant_class_en, str) or not plant_class_en.strip():
            raise ValueError("English plant class must be a non-empty string.")
        if plant_date is not None and not isinstance(plant_date, date):
            raise ValueError("plant_date must be a datetime.date object or None.")

        self.cur.execute(
            """
            INSERT INTO plants (
                plant_name_en,
                plant_class_en,
                plant_name_ja,
                plant_class_ja,
                image_path,
                botanical_name,
                location,
                plant_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """,
            (
                plant_name_en,
                plant_class_en,
                plant_name_ja,
                plant_class_ja,
                image_path,
                botanical_name,
                location,
                plant_date if plant_date else date.today(),
            ),
        )

    def delete_plant(self, plant_id):
        if not isinstance(plant_id, int):
            raise ValueError("plant_id must be an integer")

        self.cur.execute("DELETE FROM plants WHERE plant_id = %s;", (plant_id,))

    def update_plant(
        self,
        plant_id,
        plant_name_en,
        plant_class_en,
        plant_name_ja,
        plant_class_ja,
        image_path,
        botanical_name,
        location,
        plant_date=None,
    ):
        if not isinstance(plant_name_en, str) or not plant_name_en.strip():
            raise ValueError("English name must be a non-empty string.")
        if not isinstance(plant_class_en, str) or not plant_class_en.strip():
            raise ValueError("English class must be a non-empty string.")
        if not isinstance(plant_id, int):
            raise ValueError("plant_id must be an integer.")

        self.cur.execute(
            """
            UPDATE plants
            SET
                plant_name_en = %s,
                plant_class_en = %s,
                plant_name_ja = %s,
                plant_class_ja = %s,
                image_path = %s,
                botanical_name = %s,
                location = %s,
                plant_date = %s
            WHERE plant_id = %s;
        """,
            (
                plant_name_en,
                plant_class_en,
                plant_name_ja,
                plant_class_ja,
                image_path,
                botanical_name,
                location,
                plant_date if plant_date else date.today(),
                plant_id,
            ),
        )

    def get_all_plants(self):
        self.cur.execute(
            """
            SELECT
                plant_id,
                plant_name_en,
                plant_class_en,
                plant_name_ja,
                plant_class_ja,
                image_path,
                botanical_name,
                location,
                plant_date
            FROM plants;
        """
        )
        return self.cur.fetchall()

    def get_plant_details(self, plant_id):
        self.cur.execute(
            """
            SELECT
                plant_id,
                plant_name_en,
                plant_class_en,
                plant_name_ja,
                plant_class_ja,
                image_path,
                botanical_name,
                location,
                plant_date
            FROM plants
            WHERE plant_id = %s;
        """,
            (plant_id,),
        )
        return self.cur.fetchone()

    def list_plants_by_date(self):
        self.cur.execute(
            """
            SELECT
                plant_id,
                plant_name_en,
                plant_class_en,
                plant_name_ja,
                plant_class_ja,
                image_path,
                botanical_name,
                location,
                plant_date
            FROM plants
            ORDER BY plant_date DESC;
        """
        )
        return self.cur.fetchall()

    def search_plant_by_name(self, name, lang="en"):
        if lang == "ja":
            column = "plant_name_ja"
        else:
            column = "plant_name_en"

        self.cur.execute(
            f"""
            SELECT
                plant_id,
                plant_name_en,
                plant_class_en,
                plant_name_ja,
                plant_class_ja,
                image_path,
                botanical_name,
                location,
                plant_date
            FROM plants
            WHERE {column} ILIKE %s;
        """,
            (f"%{name}%",),
        )
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()
