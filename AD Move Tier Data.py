import sqlite3

# Database path
db_path = './pixlpets1.db'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 1: Identify moves in the `attributes` table not present in the `moves` table
cursor.execute("""
    SELECT DISTINCT attributes.value AS move_name, attributes.pet_id
    FROM attributes
    LEFT JOIN moves ON attributes.value = moves.name
    WHERE attributes.trait_type = 'Moves' AND moves.name IS NULL
""")
missing_moves = cursor.fetchall()

# Step 2: Fetch the element of each pet associated with the missing moves
for move_name, pet_id in missing_moves:
    cursor.execute("""
        SELECT value
        FROM attributes
        WHERE pet_id = ? AND trait_type = 'Element'
    """, (pet_id,))
    pet_element = cursor.fetchone()

    # Use the pet's element if found; otherwise, set to "Unknown"
    element = pet_element[0] if pet_element else "Unknown"

    # Step 3: Insert the missing move into the `moves` table with tier T0 and the pet's element
    cursor.execute("""
        INSERT INTO moves (name, element, tier)
        VALUES (?, ?, 'T0')
    """, (move_name, element))

# Commit the changes and close the connection
conn.commit()
conn.close()

"Database upgraded successfully: Missing moves added with tier T0 and associated pet elements."
