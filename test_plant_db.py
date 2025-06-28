import unittest
import uuid
from plant_db_class import PlantDB

class TestPlantDB(unittest.TestCase):

    def setUp(self):
        self.db = PlantDB()
        self.db.conn.autocommit = False

    def tearDown(self):
        self.db.conn.rollback()
        self.db.close()

    def test_insert_plant(self):
        unique_name = f"TestPlant-{uuid.uuid4()}"
        self.db.insert_plant(unique_name, "Testaceae")
        results = self.db.search_plant_by_name("TestPlant")
        self.assertTrue(any(unique_name in row for row in results))

    def test_insert_empty_name(self):
        with self.assertRaises(Exception):
            self.db.insert_plant("", "Testaceae")

    def test_insert_plant_invalid_type(self):
        with self.assertRaises(Exception):  # or TypeError / ValueError
            self.db.insert_plant(123, True)

    def test_insert_with_custom_date(self):
        from datetime import date
        custom_date = date(2023, 5, 1)
        self.db.insert_plant("Iris", "Iridaceae", custom_date)
        result = self.db.search_plant_by_name("Iris")
        self.assertTrue(result)
        self.assertEqual(result[0][3], custom_date)  # Assuming column 3 is plant_date


    def test_delete_existing_plant(self):
        self.db.insert_plant("Basil", "Lamiaceae")
        plants = self.db.get_all_plants()
        plant_id = plants[0][0]  # Assuming ID is in column 0
        self.db.delete_plant(plant_id)
        results = self.db.get_all_plants()
        self.assertFalse(any(row[0] == plant_id for row in results))

    def test_delete_nonexistent_plant(self):
        try:
            self.db.delete_plant(99999)  # Assume this ID doesn't exist
        except Exception as e:
            self.fail(f"delete_plant raised an exception unexpectedly: {e}")

    def test_delete_invalid_id_type(self):
        with self.assertRaises(Exception):
            self.db.delete_plant("invalid_id")

    def test_delete_only_one_plant(self):
        self.db.insert_plant("Lily", "Liliaceae")
        self.db.insert_plant("Daisy", "Asteraceae")
        plants = self.db.get_all_plants()
        lily_id = next(row[0] for row in plants if row[1] == "Lily")
        self.db.delete_plant(lily_id)
        remaining = self.db.get_all_plants()
        remaining_names = [row[1] for row in remaining]
        self.assertIn("Daisy", remaining_names)
        self.assertNotIn("Lily", remaining_names)

    def test_delete_none_id(self):
        with self.assertRaises(Exception):
            self.db.delete_plant(None)

    def test_delete_empty_id(self):
        with self.assertRaises(Exception):
            self.db.delete_plant("")


    def test_update_plant_success(self):
        self.db.insert_plant("OldName", "OldClass")
        plants = self.db.search_plant_by_name("OldName")
        plant_id = plants[0][0]  # Assuming plant_id is at index 0

        self.db.update_plant(plant_id, "NewName", "NewClass")
        updated = self.db.search_plant_by_name("NewName")
        self.assertTrue(any("NewName" in row for row in updated))

    def test_update_nonexistent_id(self):
        try:
            self.db.update_plant(99999, "Ghost", "Phantomaceae")  # Assume 99999 doesn't exist
        except Exception:
            self.fail("update_plant raised an exception unexpectedly")

    def test_update_invalid_id_type(self):
        with self.assertRaises(Exception):
            self.db.update_plant("not-an-id", "Name", "Class")

    def test_update_empty_name(self):
        self.db.insert_plant("TestName", "TestClass")
        plants = self.db.search_plant_by_name("TestName")
        plant_id = plants[0][0]

        with self.assertRaises(Exception):
            self.db.update_plant(plant_id, "", "TestClass")

    def test_update_to_duplicate_name(self):
        # Insert two distinct plants
        self.db.insert_plant("Unique1", "ClassA")
        self.db.insert_plant("Unique2", "ClassB")
        p1_id = self.db.search_plant_by_name("Unique1")[0][0]
        p2_id = self.db.search_plant_by_name("Unique2")[0][0]

        # Try to rename second plant to the same name as the first
        with self.assertRaises(Exception):  # Should fail due to UNIQUE constraint
            self.db.update_plant(p2_id, "Unique1", "ClassB")


    def test_get_all_plants_returns_list(self):
        results = self.db.get_all_plants()
        self.assertIsInstance(results, list)

    def test_get_all_plants_after_insert(self):
        self.db.insert_plant("Maple", "Sapindaceae")
        plants = self.db.get_all_plants()
        self.assertTrue(any("Maple" in row for row in plants))

    def test_get_all_plants_empty(self):
        plants = self.db.get_all_plants()
        self.assertEqual(plants, [])  # List should be empty at start


    def test_get_plant_details_existing(self):
        self.db.insert_plant("Daisy", "Asteraceae")
        plant = self.db.search_plant_by_name("Daisy")[0]
        plant_id = plant[0]
        details = self.db.get_plant_details(plant_id)
        self.assertEqual(details[1], "Daisy")
        self.assertEqual(details[2], "Asteraceae")

    def test_get_plant_details_nonexistent(self):
        result = self.db.get_plant_details(9999)  # ID unlikely to exist
        self.assertIsNone(result)


    def test_list_plants_by_date_empty(self):
        results = self.db.list_plants_by_date()
        self.assertEqual(results, [])

    def test_list_plants_by_date_returns_list(self):
        from datetime import date
        self.db.insert_plant("Cactus", "Cactaceae", date(2023, 1, 1))
        results = self.db.list_plants_by_date()
        self.assertIsInstance(results, list)

    def test_list_plants_by_date_ordering(self):
        from datetime import date
        # Insert with known dates
        self.db.insert_plant("Aloe", "Asphodelaceae", date(2022, 1, 1))
        self.db.insert_plant("Mint", "Lamiaceae", date(2023, 1, 1))
        self.db.insert_plant("Rose", "Rosaceae", date(2024, 1, 1))

        results = self.db.list_plants_by_date()
        names = [row[1] for row in results]  # Assuming row[1] = plant_name

        # Expect newest to oldest
        self.assertEqual(names, ["Rose", "Mint", "Aloe"])


    def test_search_exact_match(self):
        self.db.insert_plant("Tulip", "Liliaceae")
        results = self.db.search_plant_by_name("Tulip")
        self.assertTrue(any("Tulip" in row for row in results))

    def test_search_case_insensitive(self):
        self.db.insert_plant("Tulip", "Liliaceae")
        results = self.db.search_plant_by_name("tulip")  # lowercase
        self.assertTrue(any("Tulip" in row for row in results))

    def test_search_partial_match(self):
        self.db.insert_plant("Tulip", "Liliaceae")
        results = self.db.search_plant_by_name("lip")
        self.assertTrue(any("Tulip" in row for row in results))

    def test_search_multiple_matches(self):
        self.db.insert_plant("Sunflower", "Asteraceae")
        self.db.insert_plant("Sundew", "Droseraceae")
        results = self.db.search_plant_by_name("Sun")
        names = [row[1] for row in results]  # Assuming plant_name is at index 1
        self.assertIn("Sunflower", names)
        self.assertIn("Sundew", names)

    def test_search_no_results(self):
        results = self.db.search_plant_by_name("Nonexistent")
        self.assertEqual(results, [])

    def test_search_empty_string_returns_all(self):
        self.db.insert_plant("Rose", "Rosaceae")
        results = self.db.search_plant_by_name("")
        self.assertGreaterEqual(len(results), 1)

if __name__ == "__main__":
    unittest.main()
    
