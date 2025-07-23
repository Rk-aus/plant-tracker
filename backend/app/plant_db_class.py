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
            TypeError: If any input is of an incorrect type or format.
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
            TypeError: If any input is of an incorrect type or format.
            PlantNotFoundError: If no plant exists with the specified plant_id.
            UniqueBotanicalNameError: If the botanical name already exists.
            UniqueImagePathError: If the image path already exists.
                These are subclasses of UniquePlantConstraintError.
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
            TypeError: If plant_id is not a positive integer.
            PlantNotFoundError: If no plant exists with the specified plant_id.
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
        
    def get_plant_details(self, plant_id: int) -> dict:
        """
        Retrieve detailed information about a single plant by its ID, including multilingual
        name, family, and location information.

        Args:
            plant_id (int): The unique identifier of the plant.

        Returns:
            dict: A dictionary containing detailed plant information:
                - plant_id (int)
                - plant_name_en (str)
                - plant_name_ja (str)
                - family_name_en (str)
                - family_name_ja (str)
                - location_name_en (str)
                - location_name_ja (str)
                - botanical_name (str)
                - image_path (str)
                - plant_date (date)

        Raises:
            TypeError: If plant_id is not a positive integer.
            PlantNotFoundError: If no plant exists with the specified plant_id.
        """
        validate_positive_int(plant_id, "plant_id")

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    plants.plant_id,
                    plant_names.plant_name_en,
                    plant_names.plant_name_ja,
                    families.family_name_en,
                    families.family_name_ja,
                    locations.location_name_en,
                    locations.location_name_ja,
                    plants.botanical_name,
                    plants.image_path,
                    plants.plant_date
                FROM plants
                JOIN plant_names ON plants.plant_name_id = plant_names.id
                JOIN families ON plants.family_id = families.id
                JOIN locations ON plants.location_id = locations.id
                WHERE plants.plant_id = %s;
                """,
                (plant_id,),
            )
            result = cur.fetchone()
            if result is None:
                raise PlantNotFoundError(plant_id, f"No plant found with id {plant_id}")
            return result

    def search_plants(self, query: str, search_field: str, lang: str = "en") -> list[dict]:
        """
        Search for plants by name, family, or location in the specified language.

        This function performs a case-insensitive partial match (`ILIKE`) on the specified
        field using the given query string. The search is conducted in either English or 
        Japanese, depending on the selected language. The results include plant details
        along with multilingual name, family, and location information.

        Args:
            query (str): The search keyword (partial or full match).
            search_field (str): The field to search. Must be one of:
                - 'name' (plant name)
                - 'family' (family name)
                - 'location' (location name)
            lang (str, optional): Language used for the search field and results.
                Must be either 'en' (English) or 'ja' (Japanese). Defaults to 'en'.

        Returns:
            list[dict]: A list of dictionaries where each record contains:
                - plant_id (int)
                - plant_name_en (str)
                - plant_name_ja (str)
                - family_name_en (str)
                - family_name_ja (str)
                - location_name_en (str)
                - location_name_ja (str)
                - botanical_name (str)
                - image_path (str)
                - plant_date (date)

        Raises:
            ValueError: If an invalid search field is provided.
            InvalidLanguageError: If an unsupported language code is given.
        """
        valid_fields = {
            "name": {"en": "plant_name_en", "ja": "plant_name_ja"},
            "family": {"en": "family_name_en", "ja": "family_name_ja"},
            "location": {"en": "location_name_en", "ja": "location_name_ja"},
        }

        if search_field not in valid_fields:
            raise ValueError("Invalid search field.")
        if lang not in ("en", "ja"):
            raise InvalidLanguageError(lang)

        column = valid_fields[search_field][lang]

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT
                    plants.plant_id,
                    plant_names.plant_name_en,
                    plant_names.plant_name_ja,
                    families.family_name_en,
                    families.family_name_ja,
                    locations.location_name_en,
                    locations.location_name_ja,
                    plants.botanical_name,
                    plants.image_path,
                    plants.plant_date
                FROM plants
                JOIN plant_names ON plants.plant_name_id = plant_names.id
                JOIN families ON plants.family_id = families.id
                JOIN locations ON plants.location_id = locations.id
                WHERE {column} ILIKE %s
                """,
                (f"%{query}%",)
            )
            return cur.fetchall()
        
    def get_or_create_plant(self, plant_name_en: str,  plant_name_ja: str) -> int:
        """
        Retrieve the plant_id from the plant_names table if it exists,
        or insert a new entry and return its plant_id.

        Args:
            plant_name_en (str): The English name of the plant.
            plant_name_ja (str): The Japanese name of the plant.

        Returns:
            int: The corresponding plant_id, whether existing or newly created.

        Raises:
            TypeError: If plant names are empty or invalid.
            UniqueViolation: If a uniqueness constraint is violated during insertion.
        """
        validate_non_empty_str(plant_name_en, "plant_name_en")
        validate_non_empty_str(plant_name_ja, "plant_name_ja")

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT plant_id FROM plant_names 
                WHERE plant_name_en = %s AND plant_name_ja = %s;
                """,
                (plant_name_en, plant_name_ja)
            )
            result = cur.fetchone()
            if result:
                return result[0]
            
            try: 
                cur.execute(
                    """
                    INSERT INTO plant_names (plant_name_en, plant_name_ja)
                    VALUES (%s, %s)
                    RETURNING plant_id;
                    """,
                    (plant_name_en, plant_name_ja)
                )
            except pg2.errors.UniqueViolation as e:
                handle_unique_violation(e)
            return cur.fetchone()[0]

    def get_or_create_family(self, family_name_en: str, family_name_ja: str) -> int:
        """
        Retrieve the family_id from the families table if it exists,
        or insert a new entry and return its family_id.

        Args:
            family_name_en (str): Family name in English.
            family_name_ja (str): Family name in Japanese.

        Returns:
            int: Corresponding family_id. Creates a new entry if not found.

        Raises:
            TypeError: If family names are empty or invalid.
            UniqueViolation: If a uniqueness constraint is violated during insertion.
        """
        validate_non_empty_str(family_name_en, "family_name_en")
        validate_non_empty_str(family_name_ja, "family_name_ja")

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT family_id FROM families
                WHERE family_name_en = %s OR family_name_ja = %s;
                """,
                (family_name_en, family_name_ja)
            )
            result = cur.fetchone()
            if result:
                return result[0]
            
            try:
                cur.execute(
                    """
                    INSERT INTO families (family_name_en, family_name_ja)
                    VALUES (%s, %s)
                    RETURNING family_id;
                    """,
                    (family_name_en, family_name_ja)
                )
            except pg2.errors.UniqueViolation as e:
                handle_unique_violation(e)
            return cur.fetchone()[0]
            

    def get_or_create_location(self, location_name_en: str, location_name_ja: str) -> int:
        """
        Retrieve the location_id from the locations table if it exists,
        or insert a new entry and return its location_id.

        Args:
            location_name_en (str): Location name in English.
            location_name_ja (str): Location name in Japanese.

        Returns:
            int: Corresponding location_id. Creates a new entry if not found.

        Raises:
            TypeError: If location names are empty or invalid.
            UniqueViolation: If a uniqueness constraint is violated during insertion.
        """
        validate_non_empty_str(location_name_en, "location_name_en")
        validate_non_empty_str(location_name_ja, "location_name_ja")

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT location_id FROM locations
                WHERE location_name_en = %s OR location_name_ja = %s;
                """,
                (location_name_en, location_name_ja)
            )
            result = cur.fetchone()
            if result:
                return result[0]
            
            try: 
                cur.execute(
                    """
                    INSERT INTO locations (location_name_en, location_name_ja)
                    VALUES (%s, %s)
                    RETURNING location_id;
                    """,
                    (location_name_en, location_name_ja)
                )
            except pg2.errors.UniqueViolation as e:
                handle_unique_violation(e)
            return cur.fetchone()[0]



    



