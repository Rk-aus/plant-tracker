PLANT_SELECT_BASE = """
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
    JOIN plant_names ON plants.plant_name_id = plant_names.plant_name_id
    JOIN families ON plants.family_id = families.family_id
    JOIN locations ON plants.location_id = locations.location_id
"""

GET_ALL_PLANTS = PLANT_SELECT_BASE + ";"
GET_PLANT_DETAILS = PLANT_SELECT_BASE + " WHERE plants.plant_id = %s;"
LIST_PLANTS_BY_DATE = PLANT_SELECT_BASE + """
 WHERE (%(start_date)s IS NULL OR plants.plant_date >= %(start_date)s)
  AND (%(end_date)s IS NULL OR plants.plant_date <= %(end_date)s)
ORDER BY plants.plant_date DESC;
"""
SEARCH_PLANTS = PLANT_SELECT_BASE + " WHERE {column} ILIKE %s"