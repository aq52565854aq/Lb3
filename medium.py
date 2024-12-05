from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import json
import os
app = Flask(__name__)
auth = HTTPBasicAuth()

users_file = "users.json"
catalog_file = "catalog.json"

if not os.path.exists(users_file):
    users = {
        "admin": "password123",
        "user1": "mypassword",
        "test1": "newpassword"
    }
    with open(users_file, 'w') as f:
        json.dump(users, f)
else:
    with open(users_file, 'r') as f:
        users = json.load(f)

if not os.path.exists(catalog_file):
    catalog = {
        "item1": {"name": "Product1", "price": 10, "color": "red"},
        "item2": {"name": "Product2", "price": 20, "color": "blue"}
    }
    with open(catalog_file, 'w') as f:
        json.dump(catalog, f)
else:
    with open(catalog_file, 'r') as f:
        catalog = json.load(f)

@auth.verify_password
def verify_password(username, password):
    return users.get(username) == password
@app.route('/items', methods=['GET', 'POST'])
@auth.login_required
def items():
    if request.method == 'GET':

        return jsonify(catalog)

    elif request.method == 'POST':

        new_item = request.json
        item_id = new_item.get('id')
        name = new_item.get('name')
        price = new_item.get('price')
        color = new_item.get('color')

        if not item_id or not name or item_id in catalog:
            return jsonify({"error": "Item ID is required or already exists"}), 400

        catalog[item_id] = {"name": name, "price": price, "color": color}

        with open(catalog_file, 'w') as f:
            json.dump(catalog, f)

        return jsonify({"message": "Item added", "item": new_item}), 201
@app.route('/items/<string:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def item_detail(item_id):
    if request.method == 'GET':

        item = catalog.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item)

    elif request.method == 'PUT':

        updated_data = request.json
        item = catalog.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        item.update(updated_data)

        with open(catalog_file, 'w') as f:
            json.dump(catalog, f)

        return jsonify({"message": "Item updated", "item": item})

    elif request.method == 'DELETE':

        item = catalog.pop(item_id, None)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        with open(catalog_file, 'w') as f:
            json.dump(catalog, f)

        return jsonify({"message": "Item deleted"})

if __name__ == '__main__':
    app.run(debug=True)
