import unittest
import uuid
from datetime import date
from typing import Optional
from app.db.plant_db_class import PlantDB
from app.exceptions import (
    PlantNotFoundError,
    InvalidLanguageError,
    InvalidSearchFieldError,
    UniqueBotanicalNameError,
    UniqueImagePathError,
)


class TestPlantDB(unittest.TestCase):
    """
    Unit tests for the PlantDatabase class.

    This test suite verifies correct behavior of plant retrieval methods, ensuring
    they return appropriate values when the database is empty or contains data.
    """

    def setUp(self):
        self.db = PlantDB()
        self.db.conn.autocommit = False

    def tearDown(self):
        self.db.conn.rollback()
        self.db.close()

    def insert_dummy_plant(
        self,
        plant_name_en: str = "SamplePlant",
        plant_name_ja: str = "サンプル",
        plant_date: Optional[date] = None,
        image_path: str = "sample.jpg",
        botanical_name: str = "Plantus exampleus",
    ):
        """
        Inserts a dummy plant record into the database for testing purposes.

        This helper method ensures that the required foreign key dependencies 
        (plant name, family, and location) exist using get_or_create methods. 
        It is typically used in test setups to populate the database with sample data.

        Args:
            plant_name_en (str): English name of the plant. Defaults to "SamplePlant".
            plant_name_ja (str): Japanese name of the plant. Defaults to "サンプル".
            plant_date (date | None, optional): Date the plant was observed. Defaults to today if None.
            image_path (str): Filename of the plant image. Defaults to "sample.jpg".
            botanical_name (str): Scientific (botanical) name of the plant. Defaults to "Plantus exampleus".

        Returns:
            None
        """
        plant_name_id = self.db.get_or_create_plant(plant_name_en, plant_name_ja)
        family_id = self.db.get_or_create_family("Sampleaceae", "サンプル科")
        location_id = self.db.get_or_create_location("TestTown", "テスト町")

        return self.db.insert_plant(
            plant_name_id=plant_name_id,
            family_id=family_id,
            location_id=location_id,
            image_path=image_path,
            botanical_name=botanical_name,
            plant_date=plant_date or date.today(),
        )

    def test_insert(self):
        """
        Test inserting a plant and verify it can be found by search.
        Uses a unique plant name to avoid collisions.
        """
        unique_name = f"TestPlant-{uuid.uuid4()}"
        self.insert_dummy_plant(unique_name)
        results = self.db.search_plants("TestPlant", "name")
        self.assertIn(unique_name, [row["plant_name_en"] for row in results], f"Inserted plant '{unique_name}' not found in search results.")

    def test_insert_empty_image_path(self):
        """
        Test that inserting a plant with an empty image path raises a TypeError.
        """
        with self.assertRaises(TypeError):
            self.db.insert_plant(1, 1, 1, "", "BotanicalName")

    def test_insert_empty_botanical_name(self):
        """
        Test that inserting a plant with an empty botanical name raises a TypeError.
        """
        with self.assertRaises(TypeError):
            self.db.insert_plant(1, 1, 1, "some/path.jpg", "")

    def test_insert_blank_strings(self):
        """
        Test that inserting a plant with blank (whitespace only) image path or botanical name
        raises a TypeError.
        """
        with self.assertRaises(TypeError):
            self.db.insert_plant(1, 1, 1, "   ", "BotanicalName")

        with self.assertRaises(TypeError):
            self.db.insert_plant(1, 1, 1, "some/path.jpg", "   ")

    def test_insert_invalid_ids(self):
        """
        Test that inserting a plant with invalid IDs (zero or negative) raises a TypeError.
        Runs subtests for various invalid combinations.
        """
        test_cases = [
            (0, 1, 1),
            (1, 0, 1),
            (1, 1, 0),
            (-1, 2, 3),
        ]
        for plant_name_id, family_id, location_id in test_cases:
            with self.subTest(plant_name_id=plant_name_id, family_id=family_id, location_id=location_id):
                with self.assertRaises(TypeError, msg=f"Invalid IDs ({plant_name_id}, {family_id}, {location_id}) did not raise TypeError"):
                    self.db.insert_plant(plant_name_id, family_id, location_id, "path.jpg", "BotanicalName")

    def test_insert_invalid_type(self):
        """
        Test that inserting a plant with incorrect data types for any argument raises a TypeError.
        Runs subtests with various invalid input combinations.
        """
        test_cases = [
            {"plant_name_id": "not an int", "family_id": 1, "location_id": 1, "image_path": "path.jpg", "botanical_name": "Botanical", "plant_date": None},
            {"plant_name_id": 1, "family_id": "not an int", "location_id": 1, "image_path": "path.jpg", "botanical_name": "Botanical", "plant_date": None},
            {"plant_name_id": 1, "family_id": 1, "location_id": "not an int", "image_path": "path.jpg", "botanical_name": "Botanical", "plant_date": None},
            {"plant_name_id": 1, "family_id": 1, "location_id": 1, "image_path": 123, "botanical_name": "Botanical", "plant_date": None},
            {"plant_name_id": 1, "family_id": 1, "location_id": 1, "image_path": "path.jpg", "botanical_name": 456, "plant_date": None},
            {"plant_name_id": 1, "family_id": 1, "location_id": 1, "image_path": "path.jpg", "botanical_name": "Botanical", "plant_date": "not a date"},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                with self.assertRaises(TypeError, msg=f"Input {case} did not raise TypeError"):
                    self.db.insert_plant(
                        case["plant_name_id"],
                        case["family_id"],
                        case["location_id"],
                        case["image_path"],
                        case["botanical_name"],
                        case["plant_date"],
                    )

    def test_insert_duplicate_botanical_name_raises(self):
        """
        Test that inserting a plant with a duplicate botanical name raises UniqueBotanicalNameError.
        """
        botanical_name = "UniqueBotanicalName"
        self.insert_dummy_plant(plant_name_en="Plant1", botanical_name=botanical_name)

        with self.assertRaises(UniqueBotanicalNameError):
            self.insert_dummy_plant(plant_name_en="Plant2", botanical_name=botanical_name)


    def test_insert_duplicate_image_path_raises(self):
        """
        Test that inserting a plant with a duplicate image path raises UniqueImagePathError.
        """
        image_path = "unique_path.jpg"
        self.insert_dummy_plant(plant_name_en="Plant1", image_path=image_path)

        with self.assertRaises(UniqueImagePathError):
            self.insert_dummy_plant(plant_name_en="Plant2", image_path=image_path)

    def test_insert_custom_date(self):
        """
        Test that inserting a plant with a custom date correctly stores and retrieves that date.
        """
        custom_date = date(2023, 5, 1)
        self.insert_dummy_plant("Iris", plant_date=custom_date)
        results = self.db.search_plants("Iris", "name")
        self.assertGreater(len(results), 0, "No results returned for plant search")
        self.assertEqual(results[0]['plant_date'], custom_date, "Plant date does not match the custom date inserted")

    def test_update_plant_success(self):
        """Test that update_plant correctly updates all fields for an existing plant."""
        plant_name_id_old = self.db.get_or_create_plant("OldName", "古い")
        plant_name_id_new = self.db.get_or_create_plant("NewName", "新しい")
        family_id_old = self.db.get_or_create_family("OldFamily", "古い科")
        family_id_new = self.db.get_or_create_family("NewFamily", "新しい科")
        location_id_old = self.db.get_or_create_location("OldCity", "旧市")
        location_id_new = self.db.get_or_create_location("NewCity", "新市")

        self.db.insert_plant(
            plant_name_id=plant_name_id_old,
            family_id=family_id_old,
            location_id=location_id_old,
            image_path="old.jpg",
            botanical_name="OldBotanical",
            plant_date=date(2022, 5, 1),
        )
        plant = self.db.search_plants("OldName", "name")[0]
        plant_id = plant["plant_id"]

        self.db.update_plant(
            plant_id=plant_id,
            plant_name_id=plant_name_id_new,
            family_id=family_id_new,
            location_id=location_id_new,
            image_path="new.jpg",
            botanical_name="NewBotanical",
            plant_date=date(2023, 6, 1),
        )

        updated = self.db.search_plants("NewName", "name")[0]
        self.assertEqual(updated["plant_id"], plant_id, "Plant ID mismatch")
        self.assertEqual(updated["plant_name_en"], "NewName", "English name was not updated correctly")
        self.assertEqual(updated["plant_name_ja"], "新しい", "Japanese name was not updated correctly")
        self.assertEqual(updated["family_name_en"], "NewFamily", "English family name mismatch")
        self.assertEqual(updated["family_name_ja"], "新しい科", "Japanese family name mismatch")
        self.assertEqual(updated["location_name_en"], "NewCity", "English location name mismatch")
        self.assertEqual(updated["location_name_ja"], "新市", "Japanese location name mismatch")
        self.assertEqual(updated["image_path"], "new.jpg", "Image path was not updated correctly")
        self.assertEqual(updated["botanical_name"], "NewBotanical", "Botanical name mismatch")
        self.assertEqual(updated["plant_date"], "2023-06-01", "Plant date mismatch")

    def test_update_nonexistent_id(self):
        """Test that update_plant raises PlantNotFoundError when the plant_id does not exist."""
        plant_name_id = self.db.get_or_create_plant("Ghost", "ゴースト")
        family_id = self.db.get_or_create_family("Phantomaceae", "幻科")
        location_id = self.db.get_or_create_location("Void", "虚無")

        with self.assertRaises(PlantNotFoundError, msg="Expected exception not raised when updating nonexistent plant ID"):
            self.db.update_plant(
                plant_id=99999,
                plant_name_id=plant_name_id,
                family_id=family_id,
                location_id=location_id,
                image_path="ghost.jpg",
                botanical_name="Ghostus",
                plant_date=date(2022, 10, 31),
            )

    def test_update_invalid_id_type(self):
        """Test that update_plant raises TypeError when given a non-integer plant_id."""
        plant_name_id = self.db.get_or_create_plant("NewName", "新しい")
        family_id = self.db.get_or_create_family("NewFamily", "新しい科")
        location_id = self.db.get_or_create_location("NewCity", "新市")

        with self.assertRaises(TypeError, msg="Expected TypeError for non-integer plant_id"):
            self.db.update_plant(
                "not-an-id",      
                plant_name_id,
                family_id,
                location_id,
                image_path="new.jpg",
                botanical_name="NewBotanical",
                plant_date=date(2023, 6, 1),
            )

    def test_update_with_invalid_plant_name_id(self):
        """
        Test that update_plant raises a TypeError when given an invalid plant_name_id (non-integer).
            
        This ensures the method enforces correct data types for foreign key references.
        """
        self.insert_dummy_plant("TestName")
        plants = self.db.search_plants("TestName", "name")
        plant_id = plants[0]["plant_id"]
        
        with self.assertRaises(TypeError, msg="Expected TypeError for invalid plant_name_id"):
            self.db.update_plant(
                plant_id,
                "",  
                1,
                1,
                "img.jpg",
                "Botanical",
                date.today(),
            )

    def test_delete_existing_plant(self):
        """
        Test deleting an existing plant removes it from the database.
        Inserts a dummy plant first, then deletes it and verifies it's gone.
        """
        self.insert_dummy_plant("Basil")

        plants_before_delete = self.db.get_all_plants()
        self.assertTrue(plants_before_delete, "No plants found after insertion")

        plant_id = plants_before_delete[0]["plant_id"]

        self.db.delete_plant(plant_id)

        plants_after_delete = self.db.get_all_plants()

        self.assertFalse(
            any(plant["plant_id"] == plant_id for plant in plants_after_delete),
            f"Plant with id {plant_id} was not deleted"
    )

    def test_delete_nonexistent_plant(self):
        """
        Ensure deleting a non-existent plant ID does not raise an exception.
        """
        try: 
            self.db.delete_plant(99999)
        except Exception:
            self.fail("delete_plant raised an exception unexpectedly")
        

    def test_delete_invalid_id_type(self):
        """
        Test that delete_plant raises TypeError when called with invalid plant ID types.
        """
        invalid_ids = ["invalid_id", None, 12.34, [], {}, ""]
        for invalid_id in invalid_ids:
            with self.subTest(invalid_id=invalid_id):
                with self.assertRaises(TypeError, msg=f"delete_plant did not raise TypeError for ID: {invalid_id}"):
                    self.db.delete_plant(invalid_id)

    def test_delete_only_one_plant(self):
        """
        Test that deleting one specific plant removes it and leaves others intact.
        """
        self.insert_dummy_plant("Lily")
        self.insert_dummy_plant(plant_name_en="Daisy", image_path="sample2.jpg", botanical_name= "Plantus exampleus2")
        
        plants = self.db.get_all_plants()
        lily_id = next(row[0] for row in plants if row[1] == "Lily")

        self.db.delete_plant(lily_id)

        remaining = self.db.get_all_plants()
        remaining_names = [row[1] for row in remaining]

        self.assertIn("Daisy", remaining_names, "Daisy should still exist after deleting Lily")
        self.assertNotIn("Lily", remaining_names, "Lily should no longer exist after deletion")

    def test_get_all_plants_returns_list(self):
        """
        Test that get_all_plants returns a list.

        Ensures the method consistently returns a list, even if the database is empty.
        """
        results = self.db.get_all_plants()
        self.assertIsInstance(results, list, msg="Expected get_all_plants to return a list")

    def test_get_all_plants_empty(self):
        """
        Test that get_all_plants returns an empty list when no plants exist.

        Ensures that the database returns an empty result set when the plants
        table is empty, confirming correct behavior on initial state.
        """
        plants = self.db.get_all_plants()
        self.assertEqual(plants, [], msg="Expected empty list when no plants are present")

    def test_get_all_plants_after_insert(self):
        """
        Test that get_all_plants returns the newly inserted plant.

        Verifies that after inserting a plant, it appears in the results
        returned by get_all_plants.
        """
        self.insert_dummy_plant("Maple")
        plants = self.db.get_all_plants()

        self.assertTrue(
            any("Maple" in (row.get("plant_name_en") or "") for row in plants),
            msg="Expected 'Maple' to appear in get_all_plants results"
        )

    def test_get_all_plants_structure(self):
        """
        Verify the structure of each plant record returned by get_all_plants.

        Ensures that each result is a dictionary containing the expected keys,
        confirming the shape of the response matches the database schema.

        Expected keys:
            - plant_id
            - plant_name_en
            - plant_name_ja
            - family_name_en
            - family_name_ja
            - location_name_en
            - location_name_ja
            - botanical_name
            - image_path
            - plant_date
        """
        self.insert_dummy_plant("Oak")
        result = self.db.get_all_plants()[0]

        expected_keys = {
            "plant_id", "plant_name_en", "plant_name_ja",
            "family_name_en", "family_name_ja",
            "location_name_en", "location_name_ja",
            "botanical_name", "image_path", "plant_date"
        }

        self.assertTrue(
            expected_keys.issubset(result.keys()),
            msg=f"Missing keys in result: {expected_keys - set(result.keys())}"
        )

    def test_get_plant_details_existing(self):
        """
        Test that get_plant_details returns correct details for an existing plant.

        Inserts a dummy plant named "Daisy", retrieves its ID via search_plants, 
        and asserts that get_plant_details returns accurate English names 
        for plant, family, and location.
        """
        self.insert_dummy_plant("Daisy")
        plant = self.db.search_plants("Daisy", "name")[0]
        plant_id = plant["plant_id"]

        details = self.db.get_plant_details(plant_id)

        self.assertEqual(details["plant_name_en"], "Daisy", msg="Expected plant name to be 'Daisy'")
        self.assertEqual(details["family_name_en"], "Sampleaceae", msg="Expected family name to be 'Sampleaceae'")
        self.assertEqual(details["location_name_en"], "TestTown", msg="Expected location name to be 'TestTown'")

    def test_get_plant_details_nonexistent(self):
        """
        Test that get_plant_details raises PlantNotFoundError when called with a non-existent plant_id.

        Attempts to retrieve details for a plant ID that does not exist and verifies
        that the appropriate exception is raised.
        """
        with self.assertRaises(PlantNotFoundError, msg="Expected PlantNotFoundError for non-existent plant_id"):
            self.db.get_plant_details(9999)

    def test_list_plants_by_date_empty(self):
        """
        Test that list_plants_by_date returns an empty list when no plants exist.

        Ensures the method handles the empty database case gracefully.
        """
        results = self.db.list_plants_by_date()
        self.assertEqual(results, [], msg="Expected an empty list when no plants are in the database")
        self.assertIsInstance(results, list, msg="Expected result to be a list even when empty")
        self.assertEqual(len(results), 0, msg="Expected no plant records in the result")

    def test_list_plants_by_date_returns_list(self):
        """
        Test that list_plants_by_date returns a list when plants exist in the database.

        Ensures correct data structure is returned after inserting a plant.
        """
        self.insert_dummy_plant("Cactus", plant_date=date(2023, 1, 1))
        results = self.db.list_plants_by_date()
        self.assertIsInstance(results, list, msg="Expected result to be a list when plants exist")
        self.assertGreater(len(results), 0, msg="Expected at least one plant in the result")

    def test_list_plants_by_date_ordering(self):
        """
        Test that list_plants_by_date returns plants ordered by date descending.

        Verifies that the most recently added plants appear first in the result list.
        """
        self.insert_dummy_plant("Aloe", plant_date=date(2022, 1, 1))
        self.insert_dummy_plant("Mint", plant_date=date(2023, 1, 1))
        self.insert_dummy_plant("Rose", plant_date=date(2024, 1, 1))

        results = self.db.list_plants_by_date()
        plant_names = [row["plant_name_en"] for row in results]  
        expected_order = ["Rose", "Mint", "Aloe"]

        self.assertEqual(
            plant_names,
            expected_order,
            msg="Plants should be ordered from newest to oldest by plant_date"
        )
    
    def test_list_plants_same_date(self):
        """
        Test that list_plants_by_date handles multiple plants with the same date.

        The order among plants with the same date is not guaranteed unless explicitly sorted by a secondary key.
        This test verifies that all records with the same date are included in the result.
        """
        same_date = date(2024, 1, 1)
        names = ["Lavender", "Thyme", "Basil"]
        for name in names:
            self.insert_dummy_plant(name, plant_date=same_date)

        results = self.db.list_plants_by_date()
        returned_names = [row["plant_name_en"] for row in results]

        for name in names:
            self.assertIn(name, returned_names, msg=f"{name} should be present in results")

        self.assertEqual(
            sorted(returned_names),
            sorted(names),
            msg="All plants with the same date should be returned regardless of order"
        )

    def test_search_exact_match(self):
        """
        Test that the search_plants method returns the correct result
        when an exact English plant name is searched.

        This test ensures:
        - The inserted plant is returned when searched by its full name.
        - The search is case-insensitive and supports exact string matching.
        - The returned records contain the correct English plant name.
        """
        self.insert_dummy_plant("Tulip")
        results = self.db.search_plants("Tulip", search_field="name", lang="en")
        
        self.assertGreater(len(results), 0, "Expected at least one result for 'Tulip'")
        
        found = any(plant["plant_name_en"] == "Tulip" for plant in results)
        self.assertTrue(found, "Exact match for 'Tulip' not found in search results.")

    def test_search_plants_in_japanese(self):
        """
        Test searching for plants using the Japanese name field.

        This test inserts a plant with a known Japanese name and performs a partial
        match search using that Japanese string. It asserts that the correct plant
        is returned when the search is performed in Japanese.

        Ensures that:
        - The function correctly uses the Japanese column based on the lang='ja' argument.
        - Partial matching with ILIKE is working for Japanese characters.
        """
        self.insert_dummy_plant(plant_name_en="Sunflower", plant_name_ja="ヒマワリ")
        results = self.db.search_plants("ヒマ", search_field="name", lang="ja")
        self.assertTrue(any(row["plant_name_ja"] == "ヒマワリ" for row in results))

    def test_search_case_insensitive(self):
        """
        Test that plant name search is case-insensitive.

        Ensures that searching with lowercase input returns matching records
        even if the original plant name contains uppercase letters.
        """
        self.insert_dummy_plant("Tulip")
        results = self.db.search_plants("tulip", search_field="name", lang="en")

        self.assertTrue(
            any("Tulip" in row for row in results),
            msg="Expected 'Tulip' to be found in case-insensitive search results for 'tulip'."
        )

    def test_search_partial_match(self):
        """
        Test that searching by a partial string returns matching plants.

        Verifies that a substring of the plant name can be used to find
        the full plant name in the search results.
        """
        self.insert_dummy_plant("Tulip")
        results = self.db.search_plants("lip", search_field="name", lang="en")

        self.assertTrue(
            any("Tulip" in row for row in results),
            msg="Expected 'Tulip' to be found when searching with partial string 'lip'."
        )

    def test_search_multiple_matches(self):
        """
        Test that searching with a partial query returns multiple matching plants.

        Verifies that the search method returns all plants whose names partially match the query string.
        """
        self.insert_dummy_plant("Sunflower")
        self.insert_dummy_plant("Sundew")
        results = self.db.search_plants("Sun", search_field="name", lang="en")
        names = [row["plant_name_en"] for row in results]

        self.assertIn("Sunflower", names, msg="Expected 'Sunflower' to be in search results for query 'Sun'.")
        self.assertIn("Sundew", names, msg="Expected 'Sundew' to be in search results for query 'Sun'.")

    def test_search_no_results(self):
        """
        Test that searching with a query that matches no plants returns an empty list.

        Ensures the search method correctly returns no results for non-matching queries.
        """
        results = self.db.search_plants("Nonexistent", "name")
        self.assertEqual(results, [], msg="Expected empty list when no plants match the search query.")

    def test_search_empty_string_returns_all(self):
        """
        Test that searching with an empty string returns all plants.

        Verifies that an empty query returns at least the inserted plants,
        effectively retrieving all available records.
        """
        self.insert_dummy_plant("Rose")
        results = self.db.search_plants("", "name")
        self.assertGreaterEqual(len(results), 1, msg="Expected at least one plant record when searching with an empty string.")

    def test_search_invalid_search_field(self):
        """
        Test that a InvalidSearchFieldError is raised when an invalid search field is used.

        The method should only accept 'name', 'family', or 'location' as valid
        fields for searching. This test ensures that providing an unsupported
        field like 'color' triggers a proper InvalidSearchFieldError.
        """
        with self.assertRaises(InvalidSearchFieldError):
            self.db.search_plants("Tulip", search_field="color")  

    def test_search_invalid_language_code(self):
        """
        Test that a InvalidLanguageError is raised when an invalid language code is used.

        The search_plants method should only accept 'en' (English) or 'ja' (Japanese)
        as valid language codes for determining which column to search against.
        This test ensures that providing an unsupported language code like 'fr'
        results in a clear and immediate InvalidLanguageError.
        """
        with self.assertRaises(InvalidLanguageError):
            self.db.search_plants("Tulip", search_field="name", lang="fr")  

    def test_get_or_create_plant_with_empty_name(self):
        with self.assertRaises(TypeError):
            self.db.get_or_create_plant("", "サンプル")  
        
        with self.assertRaises(TypeError):
            self.db.get_or_create_plant("Sample", "")  

if __name__ == "__main__":
    unittest.main()
