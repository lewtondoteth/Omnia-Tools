import sqlite3

def upgrade_database(db_path):
    """Upgrade the database schema to improve performance."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Add indexes to optimize queries
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_trait_value ON attributes(trait_type, value);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_moves_name_tier ON moves(name, tier);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pet_moves_pet_move ON pet_moves(pet_id, move_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pets_id ON pets(id);")

        print("Indexes created successfully.")

        # Add more optimizations if needed
        # Example: Consolidate frequently joined data into a new table
        print("Creating optimized table for queries...")
        cursor.execute("DROP TABLE IF EXISTS pet_attributes_moves;")
        cursor.execute("""
        CREATE TABLE pet_attributes_moves AS
        SELECT
            pets.id AS pet_id,
            pets.image AS pet_image,
            element.value AS element,
            egg.value AS egg_status,
            GROUP_CONCAT(moves.name || ' (T' || moves.tier || ')', ', ') AS moves,
            attributes.trait_type AS trait_type,
            attributes.value AS attribute_value
        FROM pets
        LEFT JOIN attributes AS element ON pets.id = element.pet_id AND element.trait_type = 'Element'
        LEFT JOIN attributes AS egg ON pets.id = egg.pet_id AND egg.trait_type = 'Egg'
        LEFT JOIN pet_moves ON pets.id = pet_moves.pet_id
        LEFT JOIN moves ON pet_moves.move_id = moves.id
        LEFT JOIN attributes ON pets.id = attributes.pet_id
        GROUP BY pets.id, attributes.trait_type, attributes.value;
        """)

        print("Optimized table created successfully.")

        conn.commit()
    except Exception as e:
        print(f"An error occurred during the upgrade: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = "pixlpets1.db"
    upgrade_database(db_path)
    print("Database upgrade complete.")
