from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "admin": "password123",
    "user1": "mypassword",
    "test1": "newpassword"
}

catalog_dict = {
    "item1": {"name": "Product1", "price": 10, "color": "red"},
    "item2": {"name": "Product2", "price": 20, "color": "blue"}
}

@auth.verify_password
def verify_password(username, password):
    return users.get(username) == password
@app.route('/items', methods=['GET', 'POST'])
@auth.login_required
def items():
    if request.method == 'GET':

        return jsonify(catalog_dict)

    elif request.method == 'POST':

        new_item = request.json
        item_id = new_item.get('id')
        name = new_item.get('name')
        price = new_item.get('price')
        color = new_item.get('color')

        if not item_id or not name or item_id in catalog_dict:
            return jsonify({"error": "Item ID is required or already exists"}), 400

        catalog_dict[item_id] = {"name": name, "price": price, "color": color}
        return jsonify({"message": "Item added", "item": new_item}), 201
@app.route('/items/<string:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def item_detail(item_id):
    if request.method == 'GET':

        item = catalog_dict.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item)

    elif request.method == 'PUT':

        updated_data = request.json
        item = catalog_dict.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        item.update(updated_data)
        return jsonify({"message": "Item updated", "item": item})

    elif request.method == 'DELETE':

        item = catalog_dict.pop(item_id, None)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"message": "Item deleted"})

if __name__ == '__main__':
    app.run(debug=True)
