import psycopg2 as pg2
from psycopg2.extras import RealDictCursor
from datetime import date
from .connection import get_connection
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
from app.db.queries import (
    GET_ALL_PLANTS,
    GET_PLANT_DETAILS,
    LIST_PLANTS_BY_DATE,
    SEARCH_PLANTS,
)

class PlantDB:
    """
    A class to interact with the plants database.

    This class provides methods for querying and modifying plant-related data
    using a PostgreSQL connection.
    """
    def __init__(self):
        """
        Initializes the PlantDB instance and establishes a connection to the PostgreSQL database
        using credentials from environment variables.
        """
        self.conn = get_connection()

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
            cur.execute(GET_ALL_PLANTS)
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
            cur.execute(GET_PLANT_DETAILS, (plant_id,),)
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
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(LIST_PLANTS_BY_DATE, {"start_date": start_date, "end_date": end_date})
            return cur.fetchall()
        
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
        query_sql = SEARCH_PLANTS.format(column=column)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query_sql, (f"%{query}%",))
            return cur.fetchall()
        
    def _get_or_create(self, table: str, id_column: str, name_en_col: str, name_ja_col: str,
                    name_en_val: str, name_ja_val: str) -> int:
        """
        Internal helper to retrieve or insert a record into a bilingual lookup table.

        Args:
            table (str): Table name (e.g., 'plant_names').
            id_column (str): ID column to return (e.g., 'plant_id').
            name_en_col (str): English name column (e.g., 'plant_name_en').
            name_ja_col (str): Japanese name column (e.g., 'plant_name_ja').
            name_en_val (str): English name value.
            name_ja_val (str): Japanese name value.

        Returns:
            int: ID of the existing or newly inserted row.

        Raises:
            TypeError: If any name is empty or invalid.
            UniqueViolation: If a uniqueness constraint is violated during insertion.
        """
        validate_non_empty_str(name_en_val, name_en_col)
        validate_non_empty_str(name_ja_val, name_ja_col)

        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT {id_column} FROM {table}
                WHERE {name_en_col} = %s AND {name_ja_col} = %s;
                """,
                (name_en_val, name_ja_val)
            )
            result = cur.fetchone()
            if result:
                return result[0]

            try:
                cur.execute(
                    f"""
                    INSERT INTO {table} ({name_en_col}, {name_ja_col})
                    VALUES (%s, %s)
                    RETURNING {id_column};
                    """,
                    (name_en_val, name_ja_val)
                )
            except pg2.errors.UniqueViolation as e:
                handle_unique_violation(e)

            return cur.fetchone()[0]

    def get_or_create_plant(self, plant_name_en: str,  plant_name_ja: str) -> int:
        """Get or insert a plant name entry."""
        return self._get_or_create(
            table="plant_names",
            id_column="plant_id",
            name_en_col="plant_name_en",
            name_ja_col="plant_name_ja",
            name_en_val=plant_name_en,
            name_ja_val=plant_name_ja,
        )

    def get_or_create_family(self, family_name_en: str, family_name_ja: str) -> int:
        """Get or insert a family name entry."""
        return self._get_or_create(
            table="families",
            id_column="family_id",
            name_en_col="family_name_en",
            name_ja_col="family_name_ja",
            name_en_val=family_name_en,
            name_ja_val=family_name_ja,
        )
            
    def get_or_create_location(self, location_name_en: str, location_name_ja: str) -> int:
        """Get or insert a location name entry."""
        return self._get_or_create(
            table="locations",
            id_column="location_id",
            name_en_col="location_name_en",
            name_ja_col="location_name_ja",
            name_en_val=location_name_en,
            name_ja_val=location_name_ja,
        )



    



