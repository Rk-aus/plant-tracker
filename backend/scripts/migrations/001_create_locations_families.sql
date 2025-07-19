-- 1. Create locations table
CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    location_name_en TEXT NOT NULL UNIQUE,
    location_name_ja TEXT NOT NULL UNIQUE
);

-- 2. Create families table
CREATE TABLE IF NOT EXISTS families (
    family_id SERIAL PRIMARY KEY,
    family_name_en TEXT NOT NULL UNIQUE,
    family_name_ja TEXT NOT NULL UNIQUE
);

-- 3. Create plant_names table
CREATE TABLE IF NOT EXISTS plant_names (
    plant_name_id SERIAL PRIMARY KEY,
    plant_name_en TEXT NOT NULL UNIQUE,
    plant_name_ja TEXT NOT NULL UNIQUE
);

-- 4. Alter the plants table to support foreign keys
ALTER TABLE plants
    ADD COLUMN IF NOT EXISTS location_id INTEGER REFERENCES locations(location_id),
    ADD COLUMN IF NOT EXISTS family_id INTEGER REFERENCES families(family_id),
    ADD COLUMN IF NOT EXISTS plant_name_id INTEGER REFERENCES plant_names(plant_name_id);

ALTER TABLE plants DROP COLUMN location;
ALTER TABLE plants DROP COLUMN plant_name_en;
ALTER TABLE plants DROP COLUMN plant_name_ja;
ALTER TABLE plants DROP COLUMN plant_class_en;
ALTER TABLE plants DROP COLUMN plant_class_ja;
ALTER TABLE plants DROP COLUMN plant_notes;

-- 5. Make sure constraints exist on existing plant fields if retained
ALTER TABLE plants
    ALTER COLUMN plant_date SET NOT NULL;

ALTER TABLE plants
    ALTER COLUMN image_path SET NOT NULL;

ALTER TABLE plants
    ADD CONSTRAINT unique_image_path UNIQUE (image_path);

ALTER TABLE plants
    ALTER COLUMN botanical_name SET NOT NULL;

ALTER TABLE plants
    ADD CONSTRAINT unique_botanical_name UNIQUE (botanical_name);

-- You can inspect constraints like this (PostgreSQL):
-- \d plants
    
