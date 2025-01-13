import sqlite3
import datetime
import os
import requests

# Paths for the original database and backup directory
original_db = "./pixlpets1.db"
backup_dir = "./backups"
api_url = "https://www.omnia.lol/api/pixlpets"

def cleanup_old_backups(backup_dir, retention_days=30):
    """
    Deletes backups older than the specified retention period, ensuring at least one backup remains.
    """
    try:
        backups = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".db")]
        backups.sort(key=os.path.getmtime)
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        deletions = 0

        for backup in backups:
            last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(backup))
            if last_modified_time < cutoff_time and len(backups) - deletions > 1:
                os.remove(backup)
                print(f"Deleted old backup: {backup}")
                deletions += 1

        if deletions == 0:
            print("No old backups were deleted.")
        else:
            print(f"Deleted {deletions} old backups.")

    except Exception as e:
        print(f"Error during cleanup: {e}")

def create_backup(original, backup_dir):
    """
    Create a backup of the database with a timestamped filename.
    """
    try:
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_db = os.path.join(backup_dir, f"pixlpets1_backup_{timestamp}.db")
        source_conn = sqlite3.connect(original)
        dest_conn = sqlite3.connect(backup_db)

        with dest_conn:
            source_conn.backup(dest_conn)

        print(f"Backup created successfully at {backup_db}")
        return backup_db

    except sqlite3.Error as e:
        print(f"Error during backup: {e}")
        return None
    finally:
        if 'source_conn' in locals():
            source_conn.close()
        if 'dest_conn' in locals():
            dest_conn.close()

def query_unhatched_egg_ids(database_path):
    """
    Query and return IDs of pets with the attribute 'Egg = Unhatched'.
    """
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT p.id
        FROM pets p
        JOIN attributes a ON p.id = a.pet_id
        WHERE a.trait_type = 'Egg' AND a.value = 'Unhatched';
        """)
        rows = cursor.fetchall()

        return [row[0] for row in rows]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def update_pet_info(database_path, pet_id, api_response):
    """
    Update the database with information returned from the API for a pet.
    """
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Update the pets table
        cursor.execute("""
        UPDATE pets
        SET name = ?, image = ?, edition = ?, description = ?, animation_url = ?, attributes = ?
        WHERE id = ?;
        """, (
            api_response["name"],
            api_response["image"],
            api_response["edition"],
            api_response["description"],
            api_response["animation_url"],
            str(api_response["attributes"]),
            pet_id,
        ))

        # Delete old attributes
        cursor.execute("DELETE FROM attributes WHERE pet_id = ?", (pet_id,))

        # Insert updated attributes
        for attribute in api_response["attributes"]:
            cursor.execute("""
            INSERT INTO attributes (pet_id, trait_type, value)
            VALUES (?, ?, ?);
            """, (pet_id, attribute["trait_type"], attribute["value"]))

        conn.commit()
        print(f"Updated pet ID {pet_id} in the database.")

    except sqlite3.Error as e:
        print(f"Error updating pet ID {pet_id}: {e}")
    finally:
        conn.close()

def check_and_update_unhatched_pets(database_path, pet_ids):
    """
    Query the API for each unhatched pet and update the database if the pet is now hatched.
    """
    for pet_id in pet_ids:
        try:
            response = requests.get(f"{api_url}/{pet_id}")
            if response.status_code == 200:
                pet_data = response.json()

                # Check if the pet is hatched
                if any(attr["trait_type"] == "Egg" and attr["value"] == "Hatched" for attr in pet_data["attributes"]):
                    print(f"Pet ID {pet_id} is now hatched. Updating database...")
                    update_pet_info(database_path, pet_id, pet_data)
                else:
                    print(f"Pet ID {pet_id} is still unhatched.")
            else:
                print(f"Failed to fetch data for pet ID {pet_id}. Status code: {response.status_code}")

        except Exception as e:
            print(f"Error querying API for pet ID {pet_id}: {e}")

# Main execution
if __name__ == "__main__":
    # Step 1: Clean up old backups
    print("Cleaning up old backups...")
    cleanup_old_backups(backup_dir)

    # Step 2: Create a new backup
    print("Creating database backup...")
    backup_path = create_backup(original_db, backup_dir)

    if backup_path:
        # Step 3: Query unhatched pets
        print("\nQuerying unhatched pets...\n")
        unhatched_pet_ids = query_unhatched_egg_ids(backup_path)

        if unhatched_pet_ids:
            print(f"Found {len(unhatched_pet_ids)} unhatched pets. Checking their status...\n")
            check_and_update_unhatched_pets(original_db, unhatched_pet_ids)
        else:
            print("No unhatched pets found.")
    else:
        print("Backup failed. Process aborted.")
