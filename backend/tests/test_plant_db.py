import unittest
import uuid
from datetime import date
from backend.app.db.plant_db_class import PlantDB
from app.exceptions import (
    PlantNotFoundError,
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

    def insert_dummy_plant(self, name: str = "SamplePlant", plant_date: date | None = None):
        """
        Helper method to insert a dummy plant with given name and optional date.
        Uses get_or_create methods for plant, family, and location to ensure dependencies.

        Args:
            name (str): English name of the plant.
            plant_date (date | None): Optional date of the plant; defaults to today if None.

        Returns:
            None
        """
        plant_name_id = self.db.get_or_create_plant(name, "サンプル")
        family_id = self.db.get_or_create_family("Sampleaceae", "サンプル科")
        location_id = self.db.get_or_create_location("TestTown", "テスト町")

        return self.db.insert_plant(
            plant_name_id=plant_name_id,
            family_id=family_id,
            location_id=location_id,
            image_filename="sample.jpg",
            botanical_name="Plantus exampleus",
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
        self.assertIn(unique_name, [row["name"] for row in results], f"Inserted plant '{unique_name}' not found in search results.")

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

    def test_insert_custom_date(self):
        """
        Test that inserting a plant with a custom date correctly stores and retrieves that date.
        """
        custom_date = date(2023, 5, 1)
        self.insert_dummy_plant("Iris", custom_date)
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
        with self.assertDoesNotRaise():
            self.db.delete_plant(99999)

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
        self.insert_dummy_plant("Daisy")
        
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
        self.insert_dummy_plant("Cactus", date(2023, 1, 1))
        results = self.db.list_plants_by_date()
        self.assertIsInstance(results, list, msg="Expected result to be a list when plants exist")
        self.assertGreater(len(results), 0, msg="Expected at least one plant in the result")

    def test_list_plants_by_date_ordering(self):
        """
        Test that list_plants_by_date returns plants ordered by date descending.

        Verifies that the most recently added plants appear first in the result list.
        """
        self.insert_dummy_plant("Aloe", date(2022, 1, 1))
        self.insert_dummy_plant("Mint", date(2023, 1, 1))
        self.insert_dummy_plant("Rose", date(2024, 1, 1))

        results = self.db.list_plants_by_date()
        plant_names = [row[1] for row in results]  
        expected_order = ["Rose", "Mint", "Aloe"]

        self.assertEqual(
            plant_names,
            expected_order,
            msg="Plants should be ordered from newest to oldest by plant_date"
        )
        
    def test_search_exact_match(self):
        self.insert_dummy_plant("Tulip")
        results = self.db.search_plant_by_name("Tulip")
        self.assertTrue(any("Tulip" in row for row in results))

    def test_search_case_insensitive(self):
        self.insert_dummy_plant("Tulip")
        results = self.db.search_plant_by_name("tulip")
        self.assertTrue(any("Tulip" in row for row in results))

    def test_search_partial_match(self):
        self.insert_dummy_plant("Tulip")
        results = self.db.search_plant_by_name("lip")
        self.assertTrue(any("Tulip" in row for row in results))

    def test_search_multiple_matches(self):
        self.insert_dummy_plant("Sunflower")
        self.insert_dummy_plant("Sundew")
        results = self.db.search_plant_by_name("Sun")
        names = [row[1] for row in results]
        self.assertIn("Sunflower", names)
        self.assertIn("Sundew", names)

    def test_search_no_results(self):
        results = self.db.search_plant_by_name("Nonexistent")
        self.assertEqual(results, [])

    def test_search_empty_string_returns_all(self):
        self.insert_dummy_plant("Rose")
        results = self.db.search_plant_by_name("")
        self.assertGreaterEqual(len(results), 1)

    def test_get_or_create_plant_with_empty_name(self):
        with self.assertRaises(ValueError):
            self.db.get_or_create_plant("", "サンプル")  
        
        with self.assertRaises(ValueError):
            self.db.get_or_create_plant("Sample", "")  


if __name__ == "__main__":
    unittest.main()
