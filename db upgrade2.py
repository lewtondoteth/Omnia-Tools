import sqlite3
import shutil

# Define database path
db_path = "pixlpets1.db"
backup_path = "pixlpets1_backup.db"

# Step 1: Backup the existing database
shutil.copyfile(db_path, backup_path)
print(f"Backup created at {backup_path}.")

# Step 2: Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 3: Create a materialized view for simplified querying
try:
    cursor.execute("DROP VIEW IF EXISTS pets_attributes_view;")
    cursor.execute("""
        CREATE VIEW pets_attributes_view AS
        SELECT
            pets.id AS pet_id,
            GROUP_CONCAT(CASE WHEN trait_type = 'Element' THEN value END) AS element,
            GROUP_CONCAT(CASE WHEN trait_type = 'Egg' THEN value END) AS egg_status,
            GROUP_CONCAT(trait_type || ':' || value, '|') AS all_attributes
        FROM pets
        LEFT JOIN attributes ON pets.id = attributes.pet_id
        GROUP BY pets.id;
    """)
    print("Created materialized view 'pets_attributes_view'.")
except sqlite3.OperationalError as e:
    print(f"Error creating view: {e}")

# Step 4: Add indexes to optimize search queries
cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_pet_id ON attributes(pet_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_trait_type_value ON attributes(trait_type, value);")
conn.commit()
print("Indexes added to 'attributes' table.")

# Step 5: Example generalized query
example_query = """
    SELECT pet_id, element, egg_status
    FROM pets_attributes_view
    WHERE all_attributes LIKE '%Element:Fire%'
      AND all_attributes LIKE '%Egg:Hatched%'
"""
cursor.execute(example_query)
example_results = cursor.fetchall()
print("Example query results:", example_results)

# Close the connection
conn.close()
print("Database schema updated successfully!")
