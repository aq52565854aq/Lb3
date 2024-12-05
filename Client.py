import requests
from requests.auth import HTTPBasicAuth
import argparse

base_url = "http://127.0.0.1:5000/items"

auth = HTTPBasicAuth('admin', 'password123')

def check_server():
    try:
        response = requests.get(base_url, auth=auth)
        if response.status_code == 200:
            return True
        else:
            print(f"Server error, status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return False

def get_items():
    if check_server():
        response = requests.get(base_url, auth=auth)
        if response.status_code == 200:
            items = response.json()
            if isinstance(items, dict):
                print("Items in catalog:")
                for item_id, item in items.items():
                    print(f"ID: {item_id}, Name: {item['name']}, Price: {item['price']}, Color: {item['color']}")
            else:
                print("Unexpected response format, expected a dictionary.")
        else:
            print(f"Failed to fetch items. Status code: {response.status_code}")
    else:
        print("Server is not available.")

def add_item(item_id, name, price, color):
    if check_server():
        new_item = {
            "id": item_id,
            "name": name,
            "price": price,
            "color": color
        }
        response = requests.post(base_url, json=new_item, auth=auth)
        if response.status_code == 201:
            print(f"Item added: {response.json()}")
        else:
            print(f"Failed to add item. Status code: {response.status_code}, Error: {response.json()}")
    else:
        print("Server is not available.")

def update_item(item_id, name=None, price=None, color=None):
    if check_server():
        updated_data = {}
        if name:
            updated_data['name'] = name
        if price:
            updated_data['price'] = price
        if color:
            updated_data['color'] = color

        if updated_data:
            response = requests.put(f"{base_url}/{item_id}", json=updated_data, auth=auth)
            if response.status_code == 200:
                print("Item updated successfully.")
            else:
                print(f"Failed to update item. Status code: {response.status_code}, Error: {response.json()}")
        else:
            print("No data provided for update.")
    else:
        print("Server is not available.")

def delete_item(item_id):
    if check_server():
        response = requests.delete(f"{base_url}/{item_id}", auth=auth)
        if response.status_code == 200:
            print(f"Item with ID {item_id} deleted successfully.")
        else:
            print(f"Failed to delete item. Status code: {response.status_code}, Error: {response.json()}")
    else:
        print("Server is not available.")

def parse_args():
    parser = argparse.ArgumentParser(description="Client for managing items in the catalog.")
    parser.add_argument("command", choices=["get", "add", "update", "delete"], help="Command to execute")
    parser.add_argument("--item_id", type=str, help="Item ID for the operation")
    parser.add_argument("--name", type=str, help="Name of the item (for add/update)")
    parser.add_argument("--price", type=float, help="Price of the item (for add/update)")
    parser.add_argument("--color", type=str, help="Color of the item (for add/update)")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if args.command == "get":
        get_items()

    elif args.command == "add":
        if not args.item_id or not args.name or not args.price or not args.color:
            print("To add an item, item_id, name, price, and color are required.")
        else:
            add_item(args.item_id, args.name, args.price, args.color)

    elif args.command == "update":
        if not args.item_id:
            print("To update an item, item_id is required.")
        else:
            update_item(args.item_id, args.name, args.price, args.color)

    elif args.command == "delete":
        if not args.item_id:
            print("To delete an item, item_id is required.")
        else:
            delete_item(args.item_id)
