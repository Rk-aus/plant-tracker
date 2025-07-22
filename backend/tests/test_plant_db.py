import unittest
import uuid
from datetime import date
from app.plant_db_class import PlantDB


class TestPlantDB(unittest.TestCase):

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




    def test_update_plant_success(self):
        self.insert_dummy_plant("OldName")
        plants = self.db.search_plant_by_name("OldName")
        plant_id = plants[0][0]
        self.db.update_plant(
            plant_id,
            "NewName",
            "新しい",
            "NewClass",
            "新しい科",
            "new.jpg",
            "NewBotanical",
            "NewCity",
            date(2023, 6, 1),
        )
        updated = self.db.search_plant_by_name("NewName")
        self.assertTrue(any("NewName" in row for row in updated))

    def test_update_nonexistent_id(self):
        try:
            self.db.update_plant(
                99999,
                "Ghost",
                "ゴースト",
                "Phantomaceae",
                "幻科",
                "ghost.jpg",
                "Ghostus",
                "Void",
            )
        except Exception:
            self.fail("update_plant raised an exception unexpectedly")

    def test_update_invalid_id_type(self):
        with self.assertRaises(Exception):
            self.db.update_plant(
                "not-an-id",
                "Name",
                "名",
                "Class",
                "科",
                "img.jpg",
                "Botanical",
                "Place",
            )

    def test_update_empty_name(self):
        self.insert_dummy_plant("TestName")
        plants = self.db.search_plant_by_name("TestName")
        plant_id = plants[0][0]
        with self.assertRaises(Exception):
            self.db.update_plant(
                plant_id, "", "", "Class", "科", "img.jpg", "Botanical", "Place"
            )

    def test_get_all_plants_returns_list(self):
        results = self.db.get_all_plants()
        self.assertIsInstance(results, list)

    def test_get_all_plants_after_insert(self):
        self.insert_dummy_plant("Maple")
        plants = self.db.get_all_plants()
        self.assertTrue(any("Maple" in row for row in plants))

    def test_get_all_plants_empty(self):
        plants = self.db.get_all_plants()
        self.assertEqual(plants, [])

    def test_get_plant_details_existing(self):
        self.insert_dummy_plant("Daisy")
        plant = self.db.search_plant_by_name("Daisy")[0]
        plant_id = plant[0]
        details = self.db.get_plant_details(plant_id)
        self.assertEqual(details[1], "Daisy")
        self.assertEqual(details[2], "Sampleaceae")

    def test_get_plant_details_nonexistent(self):
        result = self.db.get_plant_details(9999)
        self.assertIsNone(result)

    def test_list_plants_by_date_empty(self):
        results = self.db.list_plants_by_date()
        self.assertEqual(results, [])

    def test_list_plants_by_date_returns_list(self):
        self.insert_dummy_plant("Cactus", date(2023, 1, 1))
        results = self.db.list_plants_by_date()
        self.assertIsInstance(results, list)

    def test_list_plants_by_date_ordering(self):
        self.insert_dummy_plant("Aloe", date(2022, 1, 1))
        self.insert_dummy_plant("Mint", date(2023, 1, 1))
        self.insert_dummy_plant("Rose", date(2024, 1, 1))
        results = self.db.list_plants_by_date()
        names = [row[1] for row in results]
        self.assertEqual(names, ["Rose", "Mint", "Aloe"])

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


if __name__ == "__main__":
    unittest.main()
