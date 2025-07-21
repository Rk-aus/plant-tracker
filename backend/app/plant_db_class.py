import os
import psycopg2 as pg2
from psycopg2.extras import RealDictCursor
from datetime import date
from app.utils.validators import (
    validate_positive_int,
    validate_non_empty_str,
    validate_date_or_none,
    handle_unique_violation,
)
from app.exceptions import (
    PlantNotFoundError,
    LocationNotFoundError,
    FamilyNotFoundError,
    InvalidLanguageError,
)

class PlantDB:
    def __init__(self):
        """
        Initializes the PlantDB instance and establishes a connection to the PostgreSQL database
        using credentials from environment variables.
        """
        self.conn = pg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def close(self):
        """
        Close the database connection manually.
        """
        self.conn.close()

    def insert_plant(
        self,
        plant_name_id: int,
        family_id: int,
        location_id: int,
        image_path: str,
        botanical_name: str,
        plant_date: date | None = None,
    ) -> None:
        """
        Insert a new plant record into the database.

        Args:
            plant_name_id (int): Foreign key to plant_names table.
            family_id (int): Foreign key to families table.
            location_id (int): Foreign key to locations table.
            image_path (str): Path to the plant image.
            botanical_name (str): Botanical name of the plant.
            plant_date (date | None, optional): Date associated with the plant. Defaults to today if None.

        Raises:
            ValueError: If any input validation fails.
            UniqueBotanicalNameError: If the botanical name already exists.
            UniqueImagePathError: If the image path already exists.
                These are subclasses of UniquePlantConstraintError.
        """
        validate_positive_int(plant_name_id, "plant_name_id")
        validate_positive_int(family_id, "family_id")
        validate_positive_int(location_id, "location_id")
        validate_non_empty_str(image_path, "image_path")
        validate_non_empty_str(botanical_name, "botanical_name")
        validate_date_or_none(plant_date, "plant_date")

        try:
            with self.conn.cursor() as cur:
                cur.execute(
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
        plant_id: int,
        plant_name_id: int,
        family_id: int,
        location_id: int,
        image_path: str,
        botanical_name: str,
        plant_date: date | None = None,
    ) -> None:
        """
        Update a plant record with new data.

        Args:
            plant_id (int): Unique identifier of the plant to update.
            plant_name_id (int): Foreign key to plant_names table.
            family_id (int): Foreign key to families table.
            location_id (int): Foreign key to locations table.
            image_path (str): Path to the plant image.
            botanical_name (str): Botanical name of the plant.
            plant_date (date | None, optional): Date associated with the plant. Defaults to None.

        Raises:
            PlantNotFoundError: If no plant exists with the specified plant_id.
            UniqueBotanicalNameError: If the botanical name already exists.
            UniqueImagePathError: If the image path already exists.
                These are subclasses of UniquePlantConstraintError.
            ValueError: If any input validation fails.
        """
        validate_positive_int(plant_id, "plant_id")  
        validate_positive_int(plant_name_id, "plant_name_id")
        validate_positive_int(family_id, "family_id")
        validate_positive_int(location_id, "location_id")
        validate_non_empty_str(image_path, "image_path")
        validate_non_empty_str(botanical_name, "botanical_name")
        validate_date_or_none(plant_date, "plant_date")

        try:
            with self.conn.cursor() as cur:
                cur.execute(
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
            if cur.rowcount == 0:
                raise PlantNotFoundError(plant_id, f"No plant found with ID {plant_id}.")
        except pg2.errors.UniqueViolation as e:
            handle_unique_violation(e)

    def delete_plant(self, plant_id: int) -> None:
        """
        Delete a plant record by its ID.

        Args:
            plant_id (int): The unique identifier of the plant to delete.

        Raises:
            PlantNotFoundError: If no plant exists with the specified plant_id.
            ValueError: If plant_id is not an integer.
        """
        validate_positive_int(plant_id, "plant_id")

        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM plants WHERE plant_id = %s;", (plant_id,))
            if cur.rowcount == 0:
                raise PlantNotFoundError(plant_id, f"No plant found with plant_id {plant_id}")

    def get_all_plants(self) -> list[dict]:
        """
        Retrieve all plant records without any specific order.

        Returns:
            list[dict]: List of all plant records.
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    plant_id,
                    plant_name_id,
                    family_id,
                    location_id,
                    image_path,
                    botanical_name,
                    plant_date
                FROM plants;
                """
            )
            return cur.fetchall()

    def get_plant_details(self, plant_id: int) -> dict:
        """
        Retrieve detailed information about a single plant by its ID.

        Args:
            plant_id (int): The unique identifier of the plant.

        Returns:
            dict: Plant record corresponding to the given plant_id.

        Raises:
            PlantNotFoundError: If no plant exists with the specified plant_id.
            ValueError: If plant_id is not an integer.
        """
        if not isinstance(plant_id, int):
            raise ValueError("plant_id must be an integer")

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    plant_id,
                    plant_name_id,
                    family_id,
                    location_id,
                    image_path,
                    botanical_name,
                    plant_date
                FROM plants
                WHERE plant_id = %s;
                """,
                (plant_id,),
            )
        result = cur.fetchone()
        if result is None:
            raise PlantNotFoundError(plant_id, f"No plant found with id {plant_id}")
        return result

    def list_plants_by_date(self, start_date: date | None = None, end_date: date | None = None) -> list[dict]:
        """
        Retrieve plants filtered by an optional date range, ordered by plant_date descending.

        Args:
            start_date (date | None, optional): Start date for filtering plants (inclusive). Defaults to None.
            end_date (date | None, optional): End date for filtering plants (inclusive). Defaults to None.

        Returns:
            list[dict]: List of plant records within the date range, sorted newest first.
        """
        query = """
            SELECT
                plant_id,
                plant_name_id,
                family_id,
                location_id,
                image_path,
                botanical_name,
                plant_date
            FROM plants
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND plant_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND plant_date <= %s"
            params.append(end_date)

        query += " ORDER BY plant_date DESC"

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def search_plant_by_name(self, name_query: str, lang: str = "en") -> list[dict]:
        """
        Search for plants by name in the specified language ('en' or 'ja').

        Args:
            name_query (str): The name or partial name to search for.
            lang (str): Language code, either 'en' or 'ja'. Defaults to 'en'.

        Returns:
            list[dict]: List of plants matching the search query.

        Raises:
            InvalidLanguageError: If `lang` is not 'en' or 'ja'.
        """
        columns = {"en": "plant_name_en", "ja": "plant_name_ja"}
        if lang not in columns:
            raise InvalidLanguageError(lang)
        column = columns[lang]

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                    plants.id,
                    plant_names.plant_name_en,
                    plant_names.plant_name_ja,
                    families.family_name_en,
                    families.family_name_ja,
                    plants.plant_class_en,
                    plants.plant_class_ja,
                    locations.location_name_en,
                    locations.location_name_ja,
                    plants.image_path,
                    plants.plant_date
                FROM plants
                JOIN plant_names ON plants.plant_name_id = plant_names.id
                JOIN families ON plants.family_id = families.id
                JOIN locations ON plants.location_id = locations.id
                WHERE {column} ILIKE %s
                """,
                (f"%{name_query}%",)
            )
            return cur.fetchall()
    
    def search_plant_by_family(self, family_query: str, lang: str = "en") -> list[dict]:
        """
        Search for plants by family name in the specified language ('en' or 'ja').

        Args:
            family_query (str): The family name or partial family name to search for.
            lang (str, optional): Language code, either 'en' or 'ja'. Defaults to 'en'.

        Returns:
            list[dict]: A list of plant records matching the family name query.

        Raises:
            InvalidLanguageError: If `lang` is not 'en' or 'ja'.
        """
        columns = {"en": "plant_name_en", "ja": "plant_name_ja"}
        if lang not in columns:
            raise InvalidLanguageError(lang)
        column = columns[lang]

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                    plants.id,
                    plant_names.plant_name_en,
                    plant_names.plant_name_ja,
                    families.family_name_en,
                    families.family_name_ja,
                    plants.plant_class_en,
                    plants.plant_class_ja,
                    locations.location_name_en,
                    locations.location_name_ja,
                    plants.image_path
                FROM plants
                JOIN plant_names ON plants.plant_name_id = plant_names.id
                JOIN families ON plants.family_id = families.id
                JOIN locations ON plants.location_id = locations.id
                WHERE {column} ILIKE %s
                """,
                (f"%{family_query}%",)
            )
            return cur.fetchall()
        
    def search_plant_by_location(self, location_query: str, lang: str = "en") -> list[dict]:
        """
        Search for plants by location name in the specified language ('en' or 'ja').

        Args:
            location_query (str): The location name or partial location name to search for.
            lang (str, optional): Language code, either 'en' or 'ja'. Defaults to 'en'.

        Returns:
            list[dict]: A list of plant records matching the location name query.

        Raises:
            InvalidLanguageError: If `lang` is not 'en' or 'ja'.
        """
        columns = {"en": "plant_name_en", "ja": "plant_name_ja"}
        if lang not in columns:
            raise InvalidLanguageError(lang)
        column = columns[lang]

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                    plants.id,
                    plant_names.plant_name_en,
                    plant_names.plant_name_ja,
                    families.family_name_en,
                    families.family_name_ja,
                    plants.plant_class_en,
                    plants.plant_class_ja,
                    locations.location_name_en,
                    locations.location_name_ja,
                    plants.image_path
                FROM plants
                JOIN plant_names ON plants.plant_name_id = plant_names.id
                JOIN families ON plants.family_id = families.id
                JOIN locations ON plants.location_id = locations.id
                WHERE {column} ILIKE %s
                """,
                (f"%{location_query}%",)
            )
            return cur.fetchall()
        
    def get_plant_id_by_name(self, plant_name: str, lang: str = "en") -> int:
        """
        Retrieve the plant_id from the plant_names table based on the name and language.

        Args:
            plant_name (str): The plant name in either English or Japanese.
            lang (str): 'en' or 'ja'. Defaults to 'en'.

        Returns:
            int: Corresponding plant_id.

        Raises:
            InvalidLanguageError: If `lang` is not 'en' or 'ja'.
            PlantNotFoundError: If the plant name is not found.
        """
        columns = {"en": "plant_name_en", "ja": "plant_name_ja"}
        if lang not in columns:
            raise InvalidLanguageError(lang)
        column = columns[lang]

        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT plant_id FROM plant_names WHERE {column} = %s;",
                (plant_name,)
            )
            result = cur.fetchone()
            if result is None:    
                raise PlantNotFoundError(plant_name, f"Plant name '{plant_name}' not found in {lang}.")
            return result[0]

    def get_family_id_by_name(self, family_name: str, lang: str = "en") -> int:
        """
        Retrieve the family_id from the families table based on the name and language.

        Args:
            family_name (str): The family name in English or Japanese.
            lang (str): 'en' or 'ja'. Defaults to 'en'.

        Returns:
            int: Corresponding family_id.

        Raises:
            InvalidLanguageError: If `lang` is not 'en' or 'ja'.
            FamilyNotFoundError: If the family name is not found.
        """
        columns = {"en": "family_name_en", "ja": "family_name_ja"}
        if lang not in columns:
            raise InvalidLanguageError(lang)
        column = columns[lang]

        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT family_id FROM families WHERE {column} = %s;",
                (family_name,)
            )
            result = cur.fetchone()
            if result is None:
                raise FamilyNotFoundError(family_name, f"Family name '{family_name}' not found in {lang}.")
            return result[0]

    def get_location_id_by_name(self, location_name: str, lang: str = "en") -> int:
        """
        Retrieve the location_id from the locations table based on the name and language.

        Args:
            location_name (str): The location name in English or Japanese.
            lang (str): 'en' or 'ja'. Defaults to 'en'.

        Returns:
            int: Corresponding location_id.

        Raises:
            InvalidLanguageError: If `lang` is not 'en' or 'ja'.
            LocationNotFoundError: If the location name is not found.
        """
        columns = {"en": "location_name_en", "ja": "location_name_ja"}
        if lang not in columns:
            raise InvalidLanguageError(lang)
        column = columns[lang]

        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT location_id FROM locations WHERE {column} = %s;",
                (location_name,)
            )
            result = cur.fetchone()
            if result is None:
                raise LocationNotFoundError(location_name, f"Location name '{location_name}' not found in {lang}.")
            return result[0]



    



