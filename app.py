from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

def get_unique_attributes():
    """Fetch all unique attributes and their values."""
    conn = sqlite3.connect('new_pixlpets.db')
    cursor = conn.cursor()

    # Fetch general attributes excluding moves
    cursor.execute("""
        SELECT DISTINCT
            trait_type,
            value
        FROM attributes
        WHERE trait_type != 'Moves'
        ORDER BY trait_type, value
    """)

    attributes = cursor.fetchall()

    # Fetch moves grouped by tier in descending order
    cursor.execute("""
        SELECT DISTINCT
            tier,
            name
        FROM moves
        ORDER BY tier DESC, name
    """)

    moves = cursor.fetchall()
    conn.close()

    # Organize moves into tiers
    grouped_moves = {}
    for tier, name in moves:
        grouped_moves.setdefault(f"Tier {tier}", []).append(name)

    # Combine moves with other attributes
    grouped_attributes = {}
    for trait_type, value in attributes:
        grouped_attributes.setdefault(trait_type, []).append(value)

    grouped_attributes["Moves"] = grouped_moves

    return grouped_attributes

def get_pet_details(pet_id):
    """Fetch detailed information about a specific pet."""
    conn = sqlite3.connect('new_pixlpets.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            pets.id AS id,
            pets.image AS image,
            element.value AS element,
            egg.value AS egg_status,
            (
                SELECT GROUP_CONCAT(move_name, ', ')
                FROM (
                    SELECT DISTINCT moves.name || ' (T' || moves.tier || ')' AS move_name
                    FROM pet_moves
                    JOIN moves ON pet_moves.move_id = moves.id
                    WHERE pet_moves.pet_id = pets.id
                ) AS unique_moves
            ) AS moves,
            (
                SELECT GROUP_CONCAT(attribute, '; ')
                FROM (
                    SELECT DISTINCT attributes.trait_type || ': ' || attributes.value AS attribute
                    FROM attributes
                    WHERE attributes.pet_id = pets.id
                ) AS unique_attributes
            ) AS attributes
        FROM pets
        LEFT JOIN attributes AS element ON pets.id = element.pet_id AND element.trait_type = 'Element'
        LEFT JOIN attributes AS egg ON pets.id = egg.pet_id AND egg.trait_type = 'Egg'
        WHERE pets.id = ?
        GROUP BY pets.id, pets.image, element.value, egg.value;
    """, (pet_id,))

    pet = cursor.fetchone()
    conn.close()

    if not pet:
        return None

    # Split moves into separate items and retain their formatting
    all_moves = pet["moves"].split(', ') if pet["moves"] else []

    return {
        "id": pet["id"],
        "image": pet["image"],
        "element": pet["element"],
        "is_unhatched": pet["egg_status"] != "Hatched",
        "moves": all_moves,
        "formatted_attributes": pet["attributes"].split('; ') if pet["attributes"] else []
    }

@app.route('/')
def index():
    attributes = get_unique_attributes()
    return render_template('index.html', attributes=attributes)

@app.route('/search', methods=['POST'])
def search():
    pet_id = request.form.get('pet_id')
    selected_filters = request.form.getlist('filters')

    conn = sqlite3.connect('new_pixlpets.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT
            pets.id AS pet_id,
            pets.image AS image,
            element.value AS element,
            egg.value AS egg_status,
            (
                SELECT GROUP_CONCAT(move_name, ', ')
                FROM (
                    SELECT DISTINCT moves.name || ' (T' || moves.tier || ')' AS move_name
                    FROM pet_moves
                    JOIN moves ON pet_moves.move_id = moves.id
                    WHERE pet_moves.pet_id = pets.id
                ) AS unique_moves
            ) AS moves
        FROM pets
        LEFT JOIN attributes AS element ON pets.id = element.pet_id AND element.trait_type = 'Element'
        LEFT JOIN attributes AS egg ON pets.id = egg.pet_id AND egg.trait_type = 'Egg'
    """

    conditions = []
    params = []

    if pet_id:
        conditions.append("pets.id = ?")
        params.append(pet_id)
    elif selected_filters:
        for selected_filter in selected_filters:
            trait_type, value = selected_filter.split(":", 1)
            conditions.append(
                """
                EXISTS (
                    SELECT 1 
                    FROM attributes 
                    WHERE attributes.pet_id = pets.id 
                    AND attributes.trait_type = ? 
                    AND attributes.value = ?
                )
                """
            )
            params.extend([trait_type, value])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY pets.id"

    cursor.execute(query, params)
    pets = cursor.fetchall()
    conn.close()

    attributes = get_unique_attributes()
    return render_template('index.html', attributes=attributes, pets=pets)

@app.route('/pet/<int:pet_id>')
def pet_details(pet_id):
    pet = get_pet_details(pet_id)
    if pet:
        return render_template('result.html', pet=pet)
    return render_template('result.html', error="Pet not found.")

if __name__ == '__main__':
    app.run(debug=True)
