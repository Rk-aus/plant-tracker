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

    def insert_dummy_plant(self, name="SamplePlant", plant_date=None):
        return self.db.insert_plant(
            name,
            "サンプル",
            "Sampleaceae",
            "サンプル科",
            "sample.jpg",
            "Plantus exampleus",
            "TestTown",
            plant_date or date.today(),
        )

    def test_insert_plant(self):
        unique_name = f"TestPlant-{uuid.uuid4()}"
        self.insert_dummy_plant(unique_name)
        results = self.db.search_plant_by_name("TestPlant")
        self.assertTrue(any(unique_name in row for row in results))

    def test_insert_empty_name(self):
        with self.assertRaises(Exception):
            self.db.insert_plant("", "", "Class", "", "", "", "")

    def test_insert_plant_invalid_type(self):
        with self.assertRaises(Exception):
            self.db.insert_plant(123, True, 456, False, None, None, None)

    def test_insert_with_custom_date(self):
        custom_date = date(2023, 5, 1)
        self.insert_dummy_plant("Iris", custom_date)
        result = self.db.search_plant_by_name("Iris")
        self.assertTrue(result)
        self.assertEqual(result[0][8], custom_date)

    def test_delete_existing_plant(self):
        self.insert_dummy_plant("Basil")
        plants = self.db.get_all_plants()
        plant_id = plants[0][0]
        self.db.delete_plant(plant_id)
        results = self.db.get_all_plants()
        self.assertFalse(any(row[0] == plant_id for row in results))

    def test_delete_nonexistent_plant(self):
        try:
            self.db.delete_plant(99999)
        except Exception as e:
            self.fail(f"delete_plant raised an exception unexpectedly: {e}")

    def test_delete_invalid_id_type(self):
        with self.assertRaises(Exception):
            self.db.delete_plant("invalid_id")

    def test_delete_only_one_plant(self):
        self.insert_dummy_plant("Lily")
        self.insert_dummy_plant("Daisy")
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
