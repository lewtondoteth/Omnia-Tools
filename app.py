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
    cursor.execute("SELECT * FROM pets WHERE id = ?", (pet_id,))
    pet = cursor.fetchone()
    conn.close()
    
    if pet:
        pet_dict = dict(pet)
        # Parse and format the 'attributes' field if it exists
        if 'attributes' in pet_dict:
            attributes = json.loads(pet_dict['attributes'])
            formatted_attributes = [
                f"{item['trait_type']}: {item['value']}" for item in attributes
            ]
            pet_dict['formatted_attributes'] = formatted_attributes
        return render_template('result.html', pet=pet_dict)
    else:
        return render_template('result.html', error="Pet not found")

if __name__ == '__main__':
    app.run(debug=True)
