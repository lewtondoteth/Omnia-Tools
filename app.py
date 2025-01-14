from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

def get_unique_attributes():
    """Fetch all unique attributes and their values."""
    conn = sqlite3.connect('pixlpets1.db')
    cursor = conn.cursor()

    # Fetch attributes, ensuring moves are sorted by tier descending and name ascending
    cursor.execute("""
        SELECT DISTINCT
            attributes.trait_type,
            CASE
                WHEN moves.name IS NOT NULL THEN moves.name || ' (T' || COALESCE(moves.tier, '0') || ')'
                ELSE attributes.value
            END AS value,
            CAST(SUBSTR(COALESCE(moves.tier, 'T0'), 2) AS INTEGER) AS tier_number
        FROM attributes
        LEFT JOIN moves ON attributes.value = moves.name
        WHERE attributes.trait_type IS NOT NULL
        ORDER BY attributes.trait_type, tier_number DESC, attributes.value ASC
    """)

    attributes = cursor.fetchall()
    conn.close()

    # Group attributes by trait type
    grouped_attributes = {}
    for trait_type, value, tier_number in attributes:
        if trait_type and value:  # Ensure valid entries
            grouped_attributes.setdefault(trait_type, []).append(value)

    return grouped_attributes


    attributes = cursor.fetchall()
    conn.close()

    # Group attributes by trait type
    grouped_attributes = {}
    for trait_type, value, tier_number in attributes:
        if trait_type and value:  # Ensure valid entries
            grouped_attributes.setdefault(trait_type, []).append(value)

    return grouped_attributes

def get_pet_details(pet_id):
    """Fetch detailed information about a specific pet."""
    conn = sqlite3.connect('pixlpets1.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Query for pet and its attributes
    cursor.execute("""
        SELECT pets.id AS id, pets.image AS image,
               element.value AS element,
               egg.value AS egg_status,
               GROUP_CONCAT(moves.name || ' (T' || moves.tier || ')', ', ') AS moves
        FROM pets
        LEFT JOIN attributes AS element ON pets.id = element.pet_id AND element.trait_type = 'Element'
        LEFT JOIN attributes AS egg ON pets.id = egg.pet_id AND egg.trait_type = 'Egg'
        LEFT JOIN pet_moves ON pets.id = pet_moves.pet_id
        LEFT JOIN moves ON pet_moves.move_id = moves.id
        WHERE pets.id = ?
        GROUP BY pets.id
        ORDER BY moves.tier DESC
    """, (pet_id,))
    pet = cursor.fetchone()

    # Query for additional attributes
    cursor.execute("""
        SELECT trait_type, value
        FROM attributes
        WHERE pet_id = ?
    """, (pet_id,))
    attributes = cursor.fetchall()
    conn.close()

    if pet:
        return {
            "id": pet["id"],
            "image": pet["image"],
            "element": pet["element"],
            "is_unhatched": pet["egg_status"] != "Hatched",
            "moves": pet["moves"].split(", ") if pet["moves"] else [],
            "formatted_attributes": [f"{row['trait_type']}: {row['value']}" for row in attributes]
        }
    return None

@app.route('/')
def index():
    attributes = get_unique_attributes()
    return render_template('index.html', attributes=attributes)

@app.route('/search', methods=['POST'])
def search():
    pet_id = request.form.get('pet_id')  # Use form-encoded data
    selected_filters = request.form.getlist('filters')  # Retrieve filters as a list

    conn = sqlite3.connect('pixlpets1.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT pets.id AS pet_id, pets.image AS image,
               element.value AS element,
               egg.value AS egg_status,
               GROUP_CONCAT(moves.name || ' (T' || moves.tier || ')', ', ') AS moves
        FROM pets
        LEFT JOIN attributes AS element ON pets.id = element.pet_id AND element.trait_type = 'Element'
        LEFT JOIN attributes AS egg ON pets.id = egg.pet_id AND egg.trait_type = 'Egg'
        LEFT JOIN pet_moves ON pets.id = pet_moves.pet_id
        LEFT JOIN moves ON pet_moves.move_id = moves.id
    """

    conditions = []
    params = []

    if pet_id:
        conditions.append("pets.id = ?")
        params.append(pet_id)
    elif selected_filters:
        filter_conditions = []
        for selected_filter in selected_filters:
            trait_type, value = selected_filter.split(":")
            filter_conditions.append("(attributes.trait_type = ? AND attributes.value = ?)")
            params.extend([trait_type, value])

        query += " JOIN attributes ON pets.id = attributes.pet_id"
        conditions.append("(" + " OR ".join(filter_conditions) + ")")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY pets.id ORDER BY moves.tier DESC"

    cursor.execute(query, params)
    pets = cursor.fetchall()
    conn.close()

    attributes = get_unique_attributes()
    return render_template('index.html', attributes=attributes, pets=pets)

@app.route('/pet/<int:pet_id>')
def pet_details(pet_id):
    pet = get_pet_details(pet_id)
    if pet:
        return render_template('result.html', pet=pet, element=pet["element"], is_unhatched=pet["is_unhatched"], moves=pet["moves"])
    return render_template('result.html', error="Pet not found.")

if __name__ == '__main__':
    app.run(debug=True)
