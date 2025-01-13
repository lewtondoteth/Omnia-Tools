from flask import Flask, request, render_template
import sqlite3
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    pet_id = request.form.get('pet_id')
    conn = sqlite3.connect('pixlpets1.db')
    conn.row_factory = sqlite3.Row  # Use row factory for dict-like results
    cursor = conn.cursor()

    # Fetch pet details
    cursor.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
    pet = cursor.fetchone()

    # Initialize moves and unhatched flag
    moves = []
    is_unhatched = False

    if pet:
        pet_dict = dict(pet)

        # Parse and format the 'attributes' field if it exists
        if 'attributes' in pet_dict:
            attributes = json.loads(pet_dict['attributes'])
            formatted_attributes = []
            for item in attributes:
                formatted_attributes.append(f"{item['trait_type']}: {item['value']}")
                if item['trait_type'] == 'egg' and item['value'] == 'unhatched':
                    is_unhatched = True

            pet_dict['formatted_attributes'] = formatted_attributes

        # If not unhatched, fetch moves
        if not is_unhatched:
            cursor.execute("SELECT value FROM attributes WHERE pet_id = ? AND trait_type = 'Moves'", (pet_id,))
            moves = [row[0] for row in cursor.fetchall()]

    conn.close()

    if pet:
        return render_template('result.html', pet=pet_dict, moves=moves, is_unhatched=is_unhatched)
    else:
        return render_template('result.html', error="Pet not found")

if __name__ == '__main__':
    app.run(debug=True)
