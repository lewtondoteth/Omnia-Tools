
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
        if trait_type and value:  # Ensure both trait_type and value are non-empty
            grouped_attributes.setdefault(trait_type, []).append(value)
    return grouped_attributes

def generate_correct_query(selected_attributes):
    """Generate a SQL query to ensure a pet matches all selected attributes."""
    base_query = """
        SELECT DISTINCT pets.id, pets.name, pets.image
        FROM pets
    """
    join_statements = ""
    conditions = []
    
    # Add joins for each selected attribute
    for i, attr in enumerate(selected_attributes):
        alias = f"a{i}"
        join_statements += f"""
            JOIN attributes {alias} ON pets.id = {alias}.pet_id
        """
        conditions.append(f"{alias}.value = ?")
    
    where_clause = " AND ".join(conditions)
    full_query = f"""
        {base_query}
        {join_statements}
        WHERE {where_clause}
    """
    return full_query

@app.route('/')
def index():
    attributes = get_unique_attributes()
    return render_template('index.html', attributes=attributes)

@app.route('/search', methods=['POST'])
def search():
    selected_attributes = request.form.getlist('attributes')
    pet_id = request.form.get('pet_id')
    conn = sqlite3.connect('pixlpets1.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if pet_id:
        cursor.execute("SELECT id, name, image FROM pets WHERE id = ?", (pet_id,))
        pets = cursor.fetchall()
    elif selected_attributes:
        query = generate_correct_query(selected_attributes)
        cursor.execute(query, selected_attributes)
        pets = cursor.fetchall()
    else:
        cursor.execute("SELECT id, name, image FROM pets")
        pets = cursor.fetchall()

    conn.close()
    return render_template('results.html', pets=pets)

if __name__ == '__main__':
    app.run(debug=True)
