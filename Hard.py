from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import sqlite3
import os
app = Flask(__name__)
auth = HTTPBasicAuth()

db_file = "app.db"

if not os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            color TEXT
        )
    ''')

    cursor.executemany('INSERT INTO users (username, password) VALUES (?, ?)', [
        ("admin", "password123"),
        ("user1", "mypassword")
    ])

    cursor.executemany('INSERT INTO products (id, name, price, color) VALUES (?, ?, ?, ?)', [
        ("item1", "Product1", 10, "red"),
        ("item2", "Product2", 20, "blue")
    ])
    conn.commit()
    conn.close()

@auth.verify_password
def verify_password(username, password):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == password
@app.route('/items', methods=['GET', 'POST'])
@auth.login_required
def items():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        conn.close()
        return jsonify([{"id": row[0], "name": row[1], "price": row[2], "color": row[3]} for row in products])

    elif request.method == 'POST':
        new_item = request.json
        item_id = new_item.get('id')
        name = new_item.get('name')
        price = new_item.get('price')
        color = new_item.get('color')

        if not item_id or not name or item_id_exists(item_id):
            return jsonify({"error": "Item ID is required or already exists"}), 400

        cursor.execute('INSERT INTO products (id, name, price, color) VALUES (?, ?, ?, ?)',
                       (item_id, name, price, color))
        conn.commit()
        conn.close()
        return jsonify({"message": "Item added", "item": new_item}), 201
@app.route('/items/<string:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def item_detail(item_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute('SELECT * FROM products WHERE id = ?', (item_id,))
        product = cursor.fetchone()
        conn.close()
        if not product:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"id": product[0], "name": product[1], "price": product[2], "color": product[3]})

    elif request.method == 'PUT':
        updated_data = request.json
        name = updated_data.get('name')
        price = updated_data.get('price')
        color = updated_data.get('color')

        cursor.execute('UPDATE products SET name = ?, price = ?, color = ? WHERE id = ?',
                       (name, price, color, item_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Item updated"})

    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM products WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Item deleted"})

def item_id_exists(item_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM products WHERE id = ?', (item_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

if __name__ == '__main__':
    app.run(debug=True)
