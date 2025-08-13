### 2025-07-19 Normalize Schema

- Added `locations` and `families` tables.
- Linked `plants` via `location_id` and `family_id`.
- Enforced `NOT NULL` and `UNIQUE` constraints.

### 2025-08-13 Schema Update

- Moved botanical_name from plants to plant_names to enforce a one-to-one relationship between plant names and their botanical names.
