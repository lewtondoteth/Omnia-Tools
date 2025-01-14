import sqlite3
import requests

# API details
API_URL = "https://www.omnia.lol/api/pixlpets/"
DB_PATH = 'new_pixlpets.db'

def test_database_entries():
    """Test 100 random pets from the database against the API, including moves and all other data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Select 100 random pets from the database
    cursor.execute("""
    SELECT id, name, edition, description, image, animation_url
    FROM pets
    ORDER BY RANDOM()
    LIMIT 100
    """)

    pets = cursor.fetchall()

    errors = []

    for pet in pets:
        pet_id, name, edition, description, image, animation_url = pet

        try:
            # Fetch data from API
            response = requests.get(f"{API_URL}{pet_id}")
            response.raise_for_status()
            api_data = response.json()

            # Verify fields
            if api_data['name'] != name:
                errors.append(f"Pet {pet_id}: Name mismatch (DB: {name}, API: {api_data['name']})")

            if api_data['edition'] != edition:
                errors.append(f"Pet {pet_id}: Edition mismatch (DB: {edition}, API: {api_data['edition']})")

            if api_data['description'] != description:
                errors.append(f"Pet {pet_id}: Description mismatch (DB: {description}, API: {api_data['description']})")

            if api_data['image'] != image:
                errors.append(f"Pet {pet_id}: Image mismatch (DB: {image}, API: {api_data['image']})")

            if api_data['animation_url'] != animation_url:
                errors.append(f"Pet {pet_id}: Animation URL mismatch (DB: {animation_url}, API: {api_data['animation_url']})")

            # Verify attributes
            cursor.execute("""
            SELECT trait_type, value
            FROM attributes
            WHERE pet_id = ?
            """, (pet_id,))
            db_attributes = cursor.fetchall()
            
            api_attributes = {(attr['trait_type'], attr['value']) for attr in api_data['attributes']}
            if set(db_attributes) != api_attributes:
                errors.append(f"Pet {pet_id}: Attributes mismatch (DB: {db_attributes}, API: {api_attributes})")

            # Verify moves
            cursor.execute("""
            SELECT moves.name, moves.tier
            FROM moves
            JOIN pet_moves ON moves.id = pet_moves.move_id
            WHERE pet_moves.pet_id = ?
            """, (pet_id,))
            db_moves = cursor.fetchall()

            api_moves = [(attr['value'], 0) for attr in api_data['attributes'] if attr['trait_type'] == 'Moves']
            if set(db_moves) != set(api_moves):
                errors.append(f"Pet {pet_id}: Moves mismatch (DB: {db_moves}, API: {api_moves})")

        except requests.RequestException as e:
            errors.append(f"Error fetching pet {pet_id} from API: {e}")
        except Exception as e:
            errors.append(f"Unexpected error with pet {pet_id}: {e}")

    conn.close()

    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
    else:
        print("All tests passed.")

if __name__ == "__main__":
    test_database_entries()
