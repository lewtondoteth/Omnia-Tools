from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

def get_unique_attributes():
    """Fetch all unique attributes and their values."""
    conn = sqlite3.connect('pixlpets1.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT trait_type, value FROM attributes")
    attributes = cursor.fetchall()
    conn.close()
    grouped_attributes = {}
    for trait_type, value in attributes:
        if trait_type and value:
            grouped_attributes.setdefault(trait_type, []).append(value)
    return grouped_attributes

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

    pets = []
    query = """
        SELECT pets.id AS pet_id, pets.image AS image,
               element.value AS element,
               egg.value AS egg_status,
               GROUP_CONCAT(moves.value, ', ') AS moves
        FROM pets
        LEFT JOIN attributes AS element ON pets.id = element.pet_id AND element.trait_type = 'Element'
        LEFT JOIN attributes AS egg ON pets.id = egg.pet_id AND egg.trait_type = 'Egg'
        LEFT JOIN attributes AS moves ON pets.id = moves.pet_id AND moves.trait_type = 'Moves'
    """
    conditions = []
    params = []

    if pet_id:
        conditions.append("pets.id = ?")
        params.append(pet_id)
    elif selected_filters:
        filter_conditions = " OR ".join([f"all_attributes LIKE ?" for _ in selected_filters])
        conditions.append(f"({filter_conditions})")
        params.extend([f"%{filter}%" for filter in selected_filters])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY pets.id"

    cursor.execute(query, params)
    pets = cursor.fetchall()
    conn.close()

    attributes = get_unique_attributes()
    return render_template('index.html', attributes=attributes, pets=pets)

if __name__ == '__main__':
    app.run(debug=True)
