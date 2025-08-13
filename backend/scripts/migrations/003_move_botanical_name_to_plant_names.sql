-- Add new column to plant_names if it doesn't exist
ALTER TABLE plant_names
ADD COLUMN IF NOT EXISTS botanical_name TEXT;

-- Ensure column is NOT NULL
ALTER TABLE plant_names
ALTER COLUMN botanical_name SET NOT NULL;

-- Drop old constraint on plants
ALTER TABLE plants DROP CONSTRAINT IF EXISTS unique_botanical_name;

-- Add UNIQUE constraint to plant_names only if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'unique_botanical_name'
    ) THEN
        ALTER TABLE plant_names ADD CONSTRAINT unique_botanical_name UNIQUE (botanical_name);
    END IF;
END
$$;

-- Remove old column from plants
ALTER TABLE plants DROP COLUMN IF EXISTS botanical_name;
