import os
import psycopg2 as pg2
from datetime import date
from app.utils.validators import (
    validate_positive_int,
    validate_non_empty_str,
    validate_date_or_none,
    handle_unique_violation,
)

class PlantDB:
    def __init__(self):
        print("🔒 DB_PASSWORD =", os.getenv("DB_PASSWORD"))
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
        plant_name_id,
        family_id,
        location_id,
        image_path,
        botanical_name,
        plant_date=None,
    ):
        validate_positive_int(plant_name_id, "plant_name_id")
        validate_positive_int(family_id, "family_id")
        validate_positive_int(location_id, "location_id")
        validate_non_empty_str(image_path, "image_path")
        validate_non_empty_str(botanical_name, "botanical_name")
        validate_date_or_none(plant_date, "plant_date")

        try:
            self.cur.execute(
                """
                INSERT INTO plants (
                    plant_name_id,
                    family_id,
                    location_id,
                    image_path,
                    botanical_name,
                    plant_date
                ) VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (
                    plant_name_id,
                    family_id,
                    location_id,
                    image_path,
                    botanical_name,
                    plant_date or date.today(),
                ),
            )
        except pg2.errors.UniqueViolation as e:
            handle_unique_violation(e)

    def update_plant(
        self,
        plant_id,
        plant_name_id,
        family_id,
        location_id,
        image_path,
        botanical_name,
        plant_date=None,
    ):
        validate_positive_int(plant_name_id, "plant_name_id")
        validate_positive_int(family_id, "family_id")
        validate_positive_int(location_id, "location_id")
        validate_non_empty_str(image_path, "image_path")
        validate_non_empty_str(botanical_name, "botanical_name")
        validate_date_or_none(plant_date, "plant_date")

        try: 
            self.cur.execute(
                """
                UPDATE plants
                SET
                    plant_name_id = %s,
                    family_id = %s,
                    location_id = %s,
                    image_path = %s,
                    botanical_name = %s,
                    plant_date = %s
                WHERE plant_id = %s;
            """,
                (
                    plant_name_id,
                    family_id,
                    location_id,
                    image_path,
                    botanical_name,
                    plant_date or date.today(),
                    plant_id,
                ),
            )
        except pg2.errors.UniqueViolation as e:
            handle_unique_violation(e)

    def delete_plant(self, plant_id):
        if not isinstance(plant_id, int):
            raise ValueError("plant_id must be an integer")

        self.cur.execute("DELETE FROM plants WHERE plant_id = %s;", (plant_id,))

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
