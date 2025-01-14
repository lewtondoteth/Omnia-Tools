import sqlite3
import shutil

def backup_database(db_path, backup_path):
    """Backup the database file."""
    shutil.copyfile(db_path, backup_path)
    print(f"Backup created at {backup_path}")

def update_database(db_path):
    """Update the database schema to improve performance."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add indexes
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_trait_value ON attributes(trait_type, value);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_pet_id ON attributes(pet_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pets_id ON pets(id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pet_moves_pet_id ON pet_moves(pet_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_moves_id ON moves(id);")
        conn.commit()
        print("Indexes created successfully.")
    except Exception as e:
        print(f"Error creating indexes: {e}")
        conn.rollback()

    conn.close()

if __name__ == "__main__":
    db_path = "new_pixlpets.db"
    backup_path = "new_pixlpets_backup.db"

    # Backup the database
    backup_database(db_path, backup_path)

    # Update the database
    update_database(db_path)
