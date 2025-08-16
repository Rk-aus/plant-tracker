import unittest
import uuid
from datetime import date
from typing import Optional
from app.db.plant_db_class import PlantDB
from app.exceptions import (
    PlantNotFoundError,
    InvalidLanguageError,
    InvalidSearchFieldError,
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
        botanical_name: str = "Plantus exampleus",
        family_name_en: str = "Sampleaceae",
        family_name_ja: str = "サンプル科",
        location_name_en: str = "TestTown",
        location_name_ja: str = "テスト町",
        image_path: str = "sample.jpg",
        plant_date: Optional[date] = None,
    ):
        """
        Insert a dummy plant record into the database for testing purposes.

        This helper method delegates to `insert_plant_by_names` to create
        a plant entry with default or provided sample values. It is typically
        used in test setups to populate the database with known, repeatable data.

        Args:
            plant_name_en (str): English name of the plant. Defaults to "SamplePlant".
            plant_name_ja (str): Japanese name of the plant. Defaults to "サンプル".
            family_name_en (str): English family name. Defaults to "Sampleaceae".
            family_name_ja (str): Japanese family name. Defaults to "サンプル科".
            location_name_en (str): English location name. Defaults to "TestTown".
            location_name_ja (str): Japanese location name. Defaults to "テスト町".
            image_path (str): Path or filename of the plant image. Defaults to "sample.jpg".
            botanical_name (str): Scientific (botanical) name. Defaults to "Plantus exampleus".
            plant_date (date | None, optional): Date the plant was recorded.
                Defaults to today if None.

        Returns:
            int: The ID of the newly inserted dummy plant.
        """
        return self.db.insert_plant_by_names(
            plant_name_en=plant_name_en,
            plant_name_ja=plant_name_ja,
            family_name_en=family_name_en,
            family_name_ja=family_name_ja,
            location_name_en=location_name_en,
            location_name_ja=location_name_ja,
            image_path=image_path,
            botanical_name=botanical_name,
            plant_date=plant_date or date.today(),
        )
    


    def mismatch_msg(field, expected, actual):
        return f"{field} mismatch: expected {expected!r}, but got {actual!r}"




    def test_insert_plant_by_names(self):
        """
        Insert a plant using insert_plant_by_names with all existing names,
        and verify the returned plant ID is a positive integer.
        """
        self.db.insert_plant_by_names(
            plant_name_en="ExistingPlant",
            plant_name_ja="既存植物",
            botanical_name="ExistingBotanicalName",
            family_name_en="ExistingFamily",
            family_name_ja="既存科",
            location_name_en="ExistingLocation",
            location_name_ja="既存場所",
            image_path=f"preload_path_{uuid.uuid4()}.jpg",
            plant_date=date.today(),
        )

        plant_id = self.db.insert_plant_by_names(
            plant_name_en="ExistingPlant",
            plant_name_ja="既存植物",
            botanical_name="ExistingBotanicalName",
            family_name_en="ExistingFamily",
            family_name_ja="既存科",
            location_name_en="ExistingLocation",
            location_name_ja="既存場所",
            image_path=f"happy_path_{uuid.uuid4()}.jpg", 
            plant_date=date.today(),
        )

        self.assertIsInstance(
            plant_id, int,
            msg=f"Expected plant_id to be an integer, but got type: {type(plant_id).__name__}"
        )
        self.assertGreater(
            plant_id, 0,
            msg=f"Expected plant_id to be a positive integer, but got: {plant_id}"
        )

    def test_insert_name_creation(self):
        """Name creation: new names are created as needed."""
        unique_suffix = str(uuid.uuid4())
        plant_id = self.db.insert_plant_by_names(
            plant_name_en=f"NewPlant{unique_suffix}",
            plant_name_ja=f"新規植物{unique_suffix}",
            botanical_name=f"NewBotanicalName{unique_suffix}",
            family_name_en=f"NewFamily{unique_suffix}",
            family_name_ja=f"新規科{unique_suffix}",
            location_name_en=f"NewLocation{unique_suffix}",
            location_name_ja=f"新規場所{unique_suffix}",
            image_path=f"new_path_{unique_suffix}.jpg",
            plant_date=date.today(),
        )
        self.assertIsInstance(
            plant_id, int,
            msg=f"Expected plant_id to be an integer, but got type: {type(plant_id).__name__}"
        )
        self.assertGreater(
            plant_id, 0,
            msg=f"Expected plant_id to be a positive integer, but got: {plant_id}"
        )

    def test_insert_bad_types(self):
        """Passing bad argument types raises TypeError."""
        with self.assertRaises(TypeError):
            self.db.insert_plant_by_names(
                plant_name_en=123,  
                plant_name_ja="既存植物",
                family_name_en="既存科",
                family_name_ja="既存科",
                location_name_en="既存場所",
                location_name_ja="既存場所",
                image_path="bad_type.jpg",
                botanical_name="BadTypeBotanicalName",
            )

    def test_insert_constraint_violation(self):
        """Inserting duplicates triggers the expected custom exceptions."""
        image_path = "unique_image_path_for_test.jpg"

        self.db.insert_plant_by_names(
            plant_name_en="Plant1",
            plant_name_ja="植物1",
            botanical_name="UniqueBotanicalName",
            family_name_en="Family1",
            family_name_ja="科1",
            location_name_en="Location1",
            location_name_ja="場所1",
            image_path=image_path,
            plant_date=date.today(),
        )

        with self.assertRaises(UniqueImagePathError):
            self.db.insert_plant_by_names(
                plant_name_en="Plant2",
                plant_name_ja="植物2",
                botanical_name="AnotherUniqueBotanicalName",
                family_name_en="Family2",
                family_name_ja="科2",
                location_name_en="Location2",
                location_name_ja="場所2",
                image_path=image_path,
                plant_date=date.today(),
            )

    def test_insert_defaults_to_today(self):
        plant_id = self.db.insert_plant_by_names(
            plant_name_en="TodayPlant",
            plant_name_ja="今日植物",
            botanical_name="DefaultDateBotanical",
            family_name_en="TodayFamily",
            family_name_ja="今日科",
            location_name_en="TodayLocation",
            location_name_ja="今日場所",
            image_path=f"today_path_{uuid.uuid4()}.jpg",
        )
        row = self.db.get_plant_details(plant_id)  
        self.assertEqual(
            row["plant_date"],
            date.today(),
            msg=(
                f"plant_date mismatch: expected {date.today()!r}, "
                f"but received {row['plant_date']!r}"
            ),
        )

    def test_insert(self):
        """
        Test inserting a plant and verify it can be found by search.
        Uses a unique plant name to avoid collisions.
        """
        unique_name = f"TestPlant-{uuid.uuid4()}"
        self.insert_dummy_plant(unique_name)
        results = self.db.search_plants("TestPlant", "name")
        self.assertIn(unique_name, [row["plant_name_en"] for row in results], msg=f"Inserted plant '{unique_name}' not found in search results.")

    def test_insert_empty_image_path(self):
        """
        Test that inserting a plant with an empty image path raises a ValueError.
        """
        with self.assertRaises(ValueError, msg="Expected ValueError when image_path is empty"):
            self.db.insert_plant(1, 1, 1, "", "BotanicalName")

    def test_insert_blank_strings(self):
        """
        Test that inserting a plant with blank (whitespace only) image path
        raises a ValueError.
        """
        with self.assertRaises(ValueError, msg="Expected ValueError when image_path is blank"):
            self.db.insert_plant(1, 1, 1, "   ")


    def test_insert_invalid_ids(self):
        """
        Test that inserting a plant with invalid IDs (zero or negative) raises a ValueError.
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
                with self.assertRaises(
                    ValueError,
                    msg=(
                        f"Expected ValueError when inserting plant with invalid IDs: "
                        f"plant_name_id={plant_name_id}, family_id={family_id}, location_id={location_id}"
                    )
                ):
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
                input_summary = ", ".join(f"{k}={v!r}" for k, v in case.items())
                with self.assertRaises(TypeError, msg=f"Expected TypeError for input: {input_summary}"):
                    self.db.insert_plant(
                        case["plant_name_id"],
                        case["family_id"],
                        case["location_id"],
                        case["image_path"],
                        case["botanical_name"],
                        case["plant_date"],
                    )
                    
    def test_insert_duplicate_image_path_raises(self):
        """
        Test that inserting a plant with a duplicate image path raises UniqueImagePathError.
        """
        image_path = "unique_path.jpg"
        self.insert_dummy_plant(plant_name_en="Plant1", image_path=image_path)

        with self.assertRaises(UniqueImagePathError):
            self.insert_dummy_plant(plant_name_en="Plant2", plant_name_ja="サンプル２", image_path=image_path, botanical_name="Plantus exampleus2")

    def test_insert_default_date(self):
        """
        Test that inserting a plant without a custom date defaults to today's date.
        """
        today = date.today()
        self.insert_dummy_plant("Lily")  
        results = self.db.search_plants("Lily", "name")
        self.assertGreater(
            len(results), 
            0,
            msg=f"Expected at least one search result, but got 0 results for query 'Lily'"
        )
        plant_date = results[0]['plant_date']
        self.assertEqual(
            plant_date,
            today,
            msg=f"Expected plant_date to be '{today}', but got '{plant_date}'"
        )

    def test_insert_custom_date(self):
        """
        Test that inserting a plant with a custom date correctly stores and retrieves that date.
        """
        custom_date = date(2023, 5, 1)
        self.insert_dummy_plant("Iris", plant_date=custom_date)
        results = self.db.search_plants("Iris", "name")
        self.assertGreater(
            len(results), 
            0,
            msg=f"Expected at least one search result, but got 0 results for query 'Iris'"
        )
        plant_date = results[0]['plant_date']
        self.assertEqual(
            plant_date,
            custom_date,
            msg=f"Expected plant_date to be '{custom_date}', but got '{plant_date}'"
        )

    def test_insert_long_botanical_name(self):
        """
        Test inserting a plant with a long botanical name to ensure it is stored and retrieved correctly.
        """
        long_name = "A" * 255
        plant_id = self.insert_dummy_plant(botanical_name=long_name)
        botanical_name = self.db.get_plant_details(plant_id)["botanical_name"]
        self.assertEqual(
            botanical_name,
            long_name,
            msg=f"Expected botanical_name to be '{long_name}', but got '{botanical_name}'"
        )

    def test_insert_long_image_path(self):
        """
        Test inserting a plant with a long image path to ensure it is stored and retrieved correctly.
        """
        long_path = "A" * 255    
        plant_id = self.insert_dummy_plant(image_path=long_path)
        image_path = self.db.get_plant_details(plant_id)["image_path"]
        self.assertEqual(
            image_path,
            long_path,
            msg=f"Expected image_path to be '{long_path}', but got '{image_path}'"
        )
    
    def test_insert_image_path_with_special_characters(self):
        """
        Test inserting a plant with special characters in the image path.
        """
        special_path = "plant@#$.jpg"
        plant_id = self.insert_dummy_plant(image_path=special_path)
        image_path = self.db.get_plant_details(plant_id)["image_path"]
        self.assertEqual(
            image_path,
            special_path,
            msg=f"Expected image_path to be '{special_path}', but got '{image_path}'"
        )

    def test_insert_image_path_with_emoji(self):
        """
        Test inserting a plant with an emoji in the image path.
        """
        emoji_path = "images/plants/🌿_leaf.png"
        plant_id = self.insert_dummy_plant(image_path=emoji_path)
        image_path = self.db.get_plant_details(plant_id)["image_path"]
        self.assertEqual(
            image_path,
            emoji_path,
            msg=f"Expected image_path to be '{emoji_path}', but got '{image_path}'"
        )

    def test_insert_image_path_with_url(self):
        """
        Test inserting a plant with a full URL as the image path.
        """
        url_path = "http://example.com/plant.jpg"
        plant_id = self.insert_dummy_plant(image_path=url_path)
        image_path = self.db.get_plant_details(plant_id)["image_path"]
        self.assertEqual(
            image_path,
            url_path,
            msg=f"Expected image_path to be '{url_path}', but got '{image_path}'"
        )

    def test_trim_whitespace_in_botanical_name(self):
        """
        Test that leading/trailing whitespace in botanical_name is trimmed before insertion.
        """
        clean_name = "Rosa chinensis"
        name_with_whitespace = "  Rosa chinensis  "
        plant_id = self.insert_dummy_plant(botanical_name=name_with_whitespace)
        botanical_name = self.db.get_plant_details(plant_id)["botanical_name"]
        self.assertEqual(
            botanical_name,
            clean_name,
            msg=f"Expected botanical_name to be '{clean_name}', but got '{botanical_name}'"
        )

    def test_trim_whitespace_in_plant_name(self):
        """
        Test that leading/trailing whitespace in plant_name_en is trimmed before insertion.
        """
        clean_name = "Chinese rose"
        plant_name_with_whitespace = "\t Chinese rose \n"
        plant_id = self.insert_dummy_plant(plant_name_en=plant_name_with_whitespace)
        plant_name_en = self.db.get_plant_details(plant_id)["plant_name_en"]
        self.assertEqual(
            plant_name_en,
            clean_name,
            msg=f"Expected plant_name_en to be '{clean_name}', but got '{plant_name_en}'"
        )

    def test_trim_whitespace_in_image_path(self):
        """
        Test that leading/trailing whitespace in image_path is trimmed before insertion.
        """
        clean_path = "images/rose.jpg"
        path_with_whitespace = "  images/rose.jpg  "
        plant_id = self.insert_dummy_plant(image_path=path_with_whitespace)
        image_path = self.db.get_plant_details(plant_id)["image_path"]
        self.assertEqual(
            image_path,
            clean_path,
            msg=f"Expected image_path to be '{clean_path}', but got '{image_path}'"
        )

    def test_update_plant_success(self):
        """Test that update_plant correctly updates all fields for an existing plant."""
        plant_name_id_old = self.db.get_or_create_plant("OldName", "古い", "OldBotanical")
        plant_name_id_new = self.db.get_or_create_plant("NewName", "新しい", "NewBotanical")
        family_id_old = self.db.get_or_create_family("OldFamily", "古い科")
        family_id_new = self.db.get_or_create_family("NewFamily", "新しい科")
        location_id_old = self.db.get_or_create_location("OldCity", "旧市")
        location_id_new = self.db.get_or_create_location("NewCity", "新市")

        self.db.insert_plant(
            plant_name_id=plant_name_id_old,
            family_id=family_id_old,
            location_id=location_id_old,
            image_path="old.jpg",
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
            plant_date=date(2023, 6, 1),
        )

        updated = self.db.search_plants("NewName", "name")[0]
        self.assertEqual(updated["plant_id"], plant_id, msg=f"Expected plant_id to be '{plant_id}', but got '{updated['plant_id']}'")
        self.assertEqual(updated["plant_name_en"], "NewName", msg=f"Expected plant_name_en to be 'NewName', but got '{updated['plant_name_en']}'")
        self.assertEqual(updated["plant_name_ja"], "新しい", msg=f"Expected plant_name_ja to be '新しい', but got '{updated['plant_name_ja']}'")
        self.assertEqual(updated["family_name_en"], "NewFamily", msg=f"Expected family_name_en to be 'NewFamily', but got '{updated['family_name_en']}'")
        self.assertEqual(updated["family_name_ja"], "新しい科", msg=f"Expected family_name_ja to be '新しい科', but got '{updated['family_name_ja']}'")
        self.assertEqual(updated["location_name_en"], "NewCity", msg=f"Expected location_name_en to be 'NewCity', but got '{updated['location_name_en']}'")
        self.assertEqual(updated["location_name_ja"], "新市", msg=f"Expected location_name_ja to be '新市', but got '{updated['location_name_ja']}'")
        self.assertEqual(updated["image_path"], "new.jpg", msg=f"Expected image_path to be 'new.jpg', but got '{updated['image_path']}'")
        self.assertEqual(updated["botanical_name"], "NewBotanical", msg=f"Expected botanical_name to be 'NewBotanical', but got '{updated['botanical_name']}'")
        self.assertEqual(updated["plant_date"], date(2023, 6, 1), msg=f"Expected plant_date to be '{date(2023, 6, 1)}', but got '{updated['plant_date']}'")

    def test_update_nonexistent_id(self):
        """Test that update_plant raises PlantNotFoundError when the plant_id does not exist."""
        plant_name_id = self.db.get_or_create_plant("Ghost", "ゴースト", "Ghostus")
        family_id = self.db.get_or_create_family("Phantomaceae", "幻科")
        location_id = self.db.get_or_create_location("Void", "虚無")

        with self.assertRaises(PlantNotFoundError):
            self.db.update_plant(
                plant_id=99999,
                plant_name_id=plant_name_id,
                family_id=family_id,
                location_id=location_id,
                image_path="ghost.jpg",
                plant_date=date(2022, 10, 31),
            )

    def test_update_invalid_id_type(self):
        """Test that update_plant raises TypeError when given a non-integer plant_id."""
        plant_name_id = self.db.get_or_create_plant("NewName", "新しい", "Plantus novus")
        family_id = self.db.get_or_create_family("NewFamily", "新しい科")
        location_id = self.db.get_or_create_location("NewCity", "新市")

        with self.assertRaises(TypeError):
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
        
        with self.assertRaises(TypeError):
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
        self.assertTrue(
            plants_before_delete, 
            msg=f"Expected at least one plant after insertion, but got: {plants_before_delete}"
        )

        plant_id = plants_before_delete[0]["plant_id"]

        self.db.delete_plant(plant_id)

        plants_after_delete = self.db.get_all_plants()

        self.assertFalse(
            any(plant["plant_id"] == plant_id for plant in plants_after_delete),
            msg=f"Plant with id {plant_id} was not deleted"
    )

    def test_delete_nonexistent_plant_raises_error(self):
        """
        Ensure deleting a non-existent plant ID raises PlantNotFoundError.
        """
        with self.assertRaises(PlantNotFoundError):
            self.db.delete_plant(99999)

    def test_delete_invalid_id_type(self):
        """
        Test that delete_plant raises TypeError when called with invalid plant ID types.
        """
        invalid_ids = ["invalid_id", None, 12.34, [], {}, ""]
        for invalid_id in invalid_ids:
            with self.subTest(invalid_id=invalid_id):
                with self.assertRaises(TypeError, msg=f"Expected TypeError for ID: {repr(invalid_id)}"):
                    self.db.delete_plant(invalid_id)

    def test_delete_only_one_plant(self):
        """
        Test that deleting one specific plant removes it and leaves others intact.
        """
        self.insert_dummy_plant(plant_name_en="Lily")
        self.insert_dummy_plant(plant_name_en="Daisy", plant_name_ja="サンプル２", image_path="sample2.jpg", botanical_name="Plantus exampleus2")
        
        plants = self.db.get_all_plants()
        lily_id = next(row["plant_id"] for row in plants if row["plant_name_en"] == "Lily")

        self.db.delete_plant(lily_id)

        remaining = self.db.get_all_plants()
        remaining_names = [row["plant_name_en"] for row in remaining]

        self.assertIn("Daisy", remaining_names, msg="Daisy should still exist after deleting Lily")
        self.assertNotIn("Lily", remaining_names, msg="Lily should no longer exist after deletion")

    def test_get_all_plants_returns_list(self):
        """
        Test that get_all_plants returns a list.

        Ensures the method consistently returns a list, even if the database is empty.
        """
        results = self.db.get_all_plants()
        self.assertIsInstance(
            results,
            list,
            msg=f"Expected get_all_plants to return a list type, but got type: {type(results).__name__}"
        )

    def test_get_all_plants_empty(self):
        """
        Test that get_all_plants returns an empty list when no plants exist.

        Ensures that the database returns an empty result set when the plants
        table is empty, confirming correct behavior on initial state.
        """
        plants = self.db.get_all_plants()
        self.assertEqual(plants, [], msg=f"Expected an empty list, but got '{plants}'")

    def test_get_all_plants_after_insert(self):
        """
        Test that get_all_plants returns the newly inserted plant.

        Verifies that after inserting a plant, it appears in the results
        returned by get_all_plants.
        """
        self.insert_dummy_plant("Maple")
        plants = self.db.get_all_plants()

        self.assertTrue(
            any(plant["plant_name_en"] == "Maple" for plant in plants), 
            msg=f"Expected at least one plant_name_en to be 'Maple' in get_all_plants results, but got: {[row['plant_name_en'] for row in plants]}"
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

        self.assertEqual(details["plant_name_en"], "Daisy", msg=f"Expected plant_name_en to be 'Daisy', but got '{details['plant_name_en']}'")
        self.assertEqual(details["family_name_en"], "Sampleaceae", msg=f"Expected family_name_en to be 'Sampleaceae', but got '{details['family_name_en']}'")
        self.assertEqual(details["location_name_en"], "TestTown", msg=f"Expected location_name_en to be 'TestTown', but got '{details['location_name_en']}'")

    def test_get_plant_details_nonexistent(self):
        """
        Test that get_plant_details raises PlantNotFoundError when called with a non-existent plant_id.

        Attempts to retrieve details for a plant ID that does not exist and verifies
        that the appropriate exception is raised.
        """
        with self.assertRaises(PlantNotFoundError):
            self.db.get_plant_details(9999)

    def test_list_plants_by_date_empty(self):
        """
        Test that list_plants_by_date returns an empty list when no plants exist.

        Ensures the method handles the empty database case gracefully.
        """
        results = self.db.list_plants_by_date()
        self.assertEqual(results, [], msg=f"Expected an empty list, but got '{results}'")
        self.assertIsInstance(
            results,
            list,
            msg=f"Expected list_plants_by_date to return a list type when empty, but got type: {type(results).__name__}"
        )
        self.assertEqual(len(results), 0, msg=f"Expected no plant records in the result, but got '{len(results)}'")

    def test_list_plants_by_date_returns_list(self):
        """
        Test that list_plants_by_date returns a list when plants exist in the database.

        Ensures correct data structure is returned after inserting a plant.
        """
        self.insert_dummy_plant("Cactus", plant_date=date(2023, 1, 1))
        results = self.db.list_plants_by_date()
        self.assertIsInstance(
            results,
            list,
            msg=f"Expected list_plants_by_date to return a list type when plants exist, but got type: {type(results).__name__}"
        )
        self.assertGreater(
            len(results), 
            0,
            msg="Expected at least one plant record from list_plants_by_date, but received 0 results"
        )

    def test_list_plants_by_date_ordering(self):
        """
        Test that list_plants_by_date returns plants ordered by date descending.

        Verifies that the most recently added plants appear first in the result list.
        """
        self.insert_dummy_plant("Aloe", plant_date=date(2022, 1, 1))
        self.insert_dummy_plant("Mint", plant_name_ja="サンプル２", image_path="sample2.jpg", botanical_name="Plantus exampleus2", plant_date=date(2023, 1, 1))
        self.insert_dummy_plant("Rose", plant_name_ja="サンプル３", image_path="sample3.jpg", botanical_name="Plantus exampleus3", plant_date=date(2024, 1, 1))

        results = self.db.list_plants_by_date()
        plant_names = [row["plant_name_en"] for row in results]  
        expected_order = ["Rose", "Mint", "Aloe"]

        self.assertEqual(
            plant_names,
            expected_order,
            msg=(
                f"Expected plant names ordered as {expected_order}, "
                f"but got {plant_names}"
            )
        )

    def test_list_plants_same_date(self):
        """
        Test that list_plants_by_date handles multiple plants with the same date.

        The order among plants with the same date is not guaranteed unless explicitly sorted by a secondary key.
        This test verifies that all records with the same date are included in the result.
        """
        same_date = date(2024, 1, 1)
        names = ["Lavender", "Thyme", "Basil"]
        self.insert_dummy_plant("Lavender", plant_date=same_date)
        self.insert_dummy_plant("Thyme", plant_name_ja="サンプル２", image_path="sample2.jpg", botanical_name="Plantus exampleus2", plant_date=same_date)
        self.insert_dummy_plant("Basil", plant_name_ja="サンプル３", image_path="sample3.jpg", botanical_name="Plantus exampleus3", plant_date=same_date)


        results = self.db.list_plants_by_date()
        returned_names = [row["plant_name_en"] for row in results]

        for name in names:
            self.assertIn(name, returned_names, msg=f"{name} should be present in results")

        self.assertEqual(
            sorted(returned_names),
            sorted(names),            
            msg=(
                f"Expected plant names ordered as {sorted(names)}, "
                f"but got {sorted(returned_names)}"
            )
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
        
        self.assertGreater(
            len(results), 
            0,
            msg=f"Expected at least one search result, but got 0 results for query 'Tulip'"
        )
        
        self.assertTrue(
            any(plant["plant_name_en"] == "Tulip" for plant in results), 
            msg=f"Expected at least one plant_name_en to be 'Tulip' when searching with 'Tulip', but got: {[row['plant_name_en'] for row in results]}"
            )

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

        self.assertTrue(
            any(row["plant_name_ja"] == "ヒマワリ" for row in results),
            msg=f"Expected at least one plant_name_ja to be 'ヒマワリ' when searching with partial string 'ヒマ', but got: {[row['plant_name_ja'] for row in results]}"
        )

    def test_search_case_insensitive(self):
        """
        Test that plant name search is case-insensitive.

        Ensures that searching with lowercase input returns matching records
        even if the original plant name contains uppercase letters.
        """
        self.insert_dummy_plant(plant_name_en="Tulip")
        results = self.db.search_plants("tulip", search_field="name", lang="en")

        self.assertTrue(
            any(row["plant_name_en"] == "Tulip" for row in results),
            msg=f"Expected at least one plant_name_en to be 'Tulip' when searching with partial string 'lip', but got: {[row['plant_name_en'] for row in results]}"
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
            any(row["plant_name_en"] == "Tulip" for row in results),
            msg=f"Expected at least one plant_name_en to be 'Tulip' when searching with partial string 'lip', but got: {[row['plant_name_en'] for row in results]}"
        )

    def test_search_multiple_matches(self):
        """
        Test that searching with a partial query returns multiple matching plants.

        Verifies that the search method returns all plants whose names partially match the query string.
        """
        self.insert_dummy_plant(plant_name_en="Sunflower")
        self.insert_dummy_plant(plant_name_en="Sundew", plant_name_ja="サンプル２", image_path="sample2.jpg", botanical_name="Plantus exampleus2")
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
        self.assertEqual(results, [], msg=f"Expected an empty list, but got '{results}'")

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
        with self.assertRaises(ValueError, msg="Expected ValueError when plant_name_en is empty"):
            self.db.get_or_create_plant("", "サンプル", "Plantus exampleus")  
        
        with self.assertRaises(ValueError, msg="Expected ValueError when plant_name_ja is empty"):
            self.db.get_or_create_plant("Sample", "", "Plantus exampleus")  

        with self.assertRaises(ValueError, msg="Expected ValueError when plant_name_ja is empty"):
            self.db.get_or_create_plant("Sample", "サンプル", "")  

if __name__ == "__main__":
    unittest.main()
