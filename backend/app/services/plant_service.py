import psycopg2 as pg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from datetime import date
from typing import Optional
from backend.app.db.connections import get_connection, release_connection
from app.db.plant_dao import PlantDAO
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
    def __init__(self, conn, plant_dao: PlantDAO):
        self.conn = conn
        self.plant_dao = plant_dao

    def add_plant_with_related(self, plant_name_id, family_id, location_id, image_path, plant_date=None):
        try:
            plant_id = self.plant_dao.insert(
                self.conn, plant_name_id, family_id, location_id, image_path, plant_date
            )
            self.conn.commit()
            return plant_id
        except pg2.Error as e:
            self.conn.rollback()  
            raise

        # ---------- INSERT ----------
    def create_plant(
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
        """High-level plant creation logic."""
        return self.plant_dao.insert_plant_by_names(
            plant_name_en,
            plant_name_ja,
            botanical_name,
            family_name_en,
            family_name_ja,
            location_name_en,
            location_name_ja,
            image_path,
            plant_date,
        )

    # ---------- UPDATE ----------
    def update_plant(
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
        """Update an existing plant."""
        return self.plant_dao.update_plant_by_names(
            plant_id,
            plant_name_en,
            plant_name_ja,
            botanical_name,
            family_name_en,
            family_name_ja,
            location_name_en,
            location_name_ja,
            image_path,
            plant_date,
        )

    # ---------- DELETE ----------
    def delete_plant(self, plant_id: int) -> None:
        """Delete a plant by ID."""
        return self.plant_dao.delete_plant(plant_id)

    # ---------- GET ----------
    def get_all_plants(self) -> list[dict]:
        """Get all plants without ordering."""
        return self.plant_dao.get_all_plants()

    def get_plant_details(self, plant_id: int) -> dict:
        """Get detailed info about a single plant."""
        return self.plant_dao.get_plant_details(plant_id)

    def list_plants_by_date(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> list[dict]:
        """List plants filtered by date range."""
        return self.plant_dao.list_plants_by_date(start_date, end_date)

    def search_plants(
        self, query: str, search_field: str, lang: str = "en"
    ) -> list[dict]:
        """Search plants by name, family, or location."""
        return self.plant_dao.search_plants(query, search_field, lang)

    # ---------- UTILS ----------
    def ensure_plant_exists(self, plant_id: int) -> dict:
        """Utility to check if a plant exists before operations."""
        plant = self.plant_dao.get_plant_details(plant_id)
        if not plant:
            raise PlantNotFoundError(plant_id, f"No plant found with id {plant_id}")
        return plant