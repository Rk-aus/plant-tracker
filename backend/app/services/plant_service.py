"""
PlantService module.

This module defines the PlantService class, which provides a service layer
between the application (e.g., routes, controllers) and the data access layer (DAOs).
It contains business logic for managing plants, ensuring that database
connections are handled consistently and that higher-level components do not
need to interact with DAOs directly.
"""

import psycopg2 as pg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from datetime import date
from typing import Optional
from backend.app.db.connections import get_connection, release_connection
from app.db.plant_dao import PlantDAO
from app.db.connections import DatabaseConnection
from app.utils.validators.db_validators import (
    validate_positive_int, 
    validate_and_strip_str,
    validate_date_or_none,
)
from app.exceptions import (
    PlantNotFoundError,
    InvalidLanguageError,
    InvalidSearchFieldError,
    UniqueImagePathError,
)
from app.db.queries import (
    GET_ALL_PLANTS,
    GET_PLANT_DETAILS,
    LIST_PLANTS_BY_DATE,
    SEARCH_PLANTS,
)

class PlantService:
    """
    Service layer for plant-related operations.

    The PlantService class provides methods to query, insert, and manage
    plant data. It acts as an intermediary between API
    endpoints and the PlantDAO, handling database connections and
    transaction boundaries.

    Each method:
        - Opens a database connection.
        - Instantiates the appropriate DAO.
        - Calls DAO methods to perform the requested operation.
        - Releases the connection after completion.
    """
    def insert_plant_by_names(
        self,
        plant_name_en: str,
        plant_name_ja: str,
        botanical_name: str,
        family_name_en: str,
        family_name_ja: str,
        location_name_en: str,
        location_name_ja: str,
        image_path: str,
        plant_date: Optional[date] = None,
    ) -> int:
        """Insert a new plant into the database using name values instead of foreign key IDs.

        This method ensures that related records (plant name, family, location) exist, 
        retrieving their IDs if present or creating them if missing. It then inserts 
        the new plant record with the resolved foreign key IDs.

        Args:
            plant_name_en (str): English plant name.
            plant_name_ja (str): Japanese plant name.
            botanical_name (str): Botanical (scientific) name of the plant.
            family_name_en (str): English family name.
            family_name_ja (str): Japanese family name.
            location_name_en (str): English location name.
            location_name_ja (str): Japanese location name.
            image_path (str): Path to the plant image.
            plant_date (Optional[date], optional): Date the plant was recorded. 
                Defaults to today.

        Raises:
            TypeError: If an argument is of the wrong type or format.
            UniqueImagePathError: If the image path already exists.

        Returns:
            int: The ID of the newly inserted plant.
        """
        image_path = validate_and_strip_str(image_path, "image_path")
        validate_date_or_none(plant_date, "plant_date")

        with DatabaseConnection() as conn:
            try:
                plant_dao = PlantDAO(conn)

                plant_name_id = self.get_or_create_plant(plant_name_en, plant_name_ja, botanical_name, conn)
                family_id = self.get_or_create_family(family_name_en, family_name_ja, conn)
                location_id = self.get_or_create_location(location_name_en, location_name_ja, conn)
                
                validate_positive_int(plant_name_id, "plant_name_id")
                validate_positive_int(family_id, "family_id")
                validate_positive_int(location_id, "location_id")

                plant_id = plant_dao.insert_plant(
                    plant_name_id=plant_name_id,
                    family_id=family_id,
                    location_id=location_id,
                    image_path=image_path,
                    plant_date=plant_date,
                )
                conn.commit()
                return plant_id
            except Exception:
                conn.rollback()
                raise

    def update_plant_by_names(
        self,
        plant_id: int,
        plant_name_en: str,
        plant_name_ja: str,
        botanical_name: str,
        family_name_en: str,
        family_name_ja: str,
        location_name_en: str,
        location_name_ja: str,
        image_path: str,
        plant_date: Optional[date] = None,
    ) -> None:
        """Update an existing plant record using name values instead of foreign key IDs.

        This method ensures that related records (plant name, family, location) exist, 
        retrieving their IDs if present or creating them if missing. It then updates 
        the target plant record with the resolved foreign key IDs.

        Args:
            plant_id (int): Unique identifier of the plant to update.
            plant_name_en (str): English plant name.
            plant_name_ja (str): Japanese plant name.
            botanical_name (str): Botanical (scientific) name of the plant.
            family_name_en (str): English family name.
            family_name_ja (str): Japanese family name.
            location_name_en (str): English location name.
            location_name_ja (str): Japanese location name.
            image_path (str): Path to the plant image.
            plant_date (Optional[date], optional): Date associated with the plant. 
                Defaults to today.

        Raises:
            TypeError: If an argument is of the wrong type or format.
            PlantNotFoundError: If no plant exists with the specified plant_id.
            UniqueImagePathError: If the image path already exists.
        """
        validate_positive_int(plant_id, "plant_id")  
        image_path = validate_and_strip_str(image_path, "image_path")
        validate_date_or_none(plant_date, "plant_date")
        
        with DatabaseConnection() as conn:
            try:
                plant_dao = PlantDAO(conn)

                plant_name_id = self.get_or_create_plant(plant_name_en, plant_name_ja, botanical_name, conn)
                family_id = self.get_or_create_family(family_name_en, family_name_ja, conn)
                location_id = self.get_or_create_location(location_name_en, location_name_ja, conn)
                
                validate_positive_int(plant_name_id, "plant_name_id")
                validate_positive_int(family_id, "family_id")
                validate_positive_int(location_id, "location_id")

                plant_dao.update_plant(
                    plant_id=plant_id,
                    plant_name_id=plant_name_id,
                    family_id=family_id,
                    location_id=location_id,
                    image_path=image_path,
                    plant_date=plant_date,
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise

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
                - botanical_name (str)
                - family_name_en (str)
                - family_name_ja (str)
                - location_name_en (str)
                - location_name_ja (str)
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

    def list_plants_by_date(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> list[dict]:
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
                - botanical_name (str)
                - family_name_en (str)
                - family_name_ja (str)
                - location_name_en (str)
                - location_name_ja (str)
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
            raise InvalidSearchFieldError("Invalid search field.")
        if lang not in ("en", "ja"):
            raise InvalidLanguageError(lang)

        column = valid_fields[search_field][lang]
        query_sql = SEARCH_PLANTS.format(column=column)

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query_sql, (f"%{query}%",))
            return cur.fetchall()

    def get_or_create_plant(self, plant_name_en: str, plant_name_ja: str, botanical_name: str) -> int:
        """Get or insert a plant name entry with botanical name."""
        plant_name_en = validate_and_strip_str(plant_name_en, "plant_name_en")
        plant_name_ja = validate_and_strip_str(plant_name_ja, "plant_name_ja")
        botanical_name = validate_and_strip_str(botanical_name, "botanical_name")

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT plant_name_id FROM plant_names
                WHERE plant_name_en = %s AND plant_name_ja = %s AND botanical_name = %s;
            """, (plant_name_en, plant_name_ja, botanical_name))
            result = cur.fetchone()
            if result:
                return result[0]

            try:
                cur.execute("""
                    INSERT INTO plant_names (plant_name_en, plant_name_ja, botanical_name)
                    VALUES (%s, %s, %s)
                    RETURNING plant_name_id;
                """, (plant_name_en, plant_name_ja, botanical_name))
            except pg2.errors.UniqueViolation:
                raise UniqueImagePathError("Image path already exists.")

            return cur.fetchone()[0]
        
    def _get_or_create(
        self,
        table: str,
        id_column: str,
        name_en_col: str,
        name_ja_col: str,
        name_en_val: str,
        name_ja_val: str
    ) -> int:
        """
        Internal helper to retrieve or insert a record into a bilingual lookup table.

        Args:
            table (str): Table name (e.g., 'families').
            id_column (str): ID column to return (e.g., 'family_id').
            name_en_col (str): English name column (e.g., 'family_name_en').
            name_ja_col (str): Japanese name column (e.g., 'family_name_ja').
            name_en_val (str): English name value.
            name_ja_val (str): Japanese name value.

        Returns:
            int: ID of the existing or newly inserted row.

        Raises:
            TypeError: If any name is empty or invalid.
            UniqueViolation: If a uniqueness constraint is violated during insertion.
        """
        name_en_val = validate_and_strip_str(name_en_val, name_en_col)
        name_ja_val = validate_and_strip_str(name_ja_val, name_ja_col)

        with self.conn.cursor() as cur:
            select_query = sql.SQL("""
                SELECT {id_column}
                FROM {table}
                WHERE {name_en_col} = %s AND {name_ja_col} = %s;
            """).format(
                id_column=sql.Identifier(id_column),
                table=sql.Identifier(table),
                name_en_col=sql.Identifier(name_en_col),
                name_ja_col=sql.Identifier(name_ja_col)
            )

            cur.execute(select_query, (name_en_val, name_ja_val))
            result = cur.fetchone()
            if result:
                return result[0]

            insert_query = sql.SQL("""
                INSERT INTO {table} ({name_en_col}, {name_ja_col})
                VALUES (%s, %s)
                RETURNING {id_column};
            """).format(
                table=sql.Identifier(table),
                name_en_col=sql.Identifier(name_en_col),
                name_ja_col=sql.Identifier(name_ja_col),
                id_column=sql.Identifier(id_column)
            )

            try:
                cur.execute(insert_query, (name_en_val, name_ja_val))
            except pg2.errors.UniqueViolation:
                raise UniqueImagePathError("Image path already exists.")

            return cur.fetchone()[0]

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