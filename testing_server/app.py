from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime

app = Flask(__name__)


def load_data():
    try:
        with open('./data/data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"data": []}


def save_data(data):
    with open('./data/data.json', 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/')
def index():
    return render_template('table.html')


@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        data = load_data()
        return jsonify(data)
    elif request.method == 'POST':
        new_data = request.json
        save_data(new_data)
        return jsonify({"message": "Data updated successfully"}), 200


@app.route('/api/add_item', methods=['POST'])
def add_item():
    new_item = request.json
    data = load_data()
    new_id = max([item['id'] for item in data['data']] + [0]) + 1
    new_item['id'] = new_id
    new_item['lastUpdate'] = datetime.now().isoformat()
    data['data'].append(new_item)
    save_data(data)
    return jsonify({"message": "Item added successfully", "item": new_item}), 201


@app.route('/api/update_item/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    updated_item = request.json
    data = load_data()
    for i, item in enumerate(data['data']):
        if item['id'] == item_id:
            data['data'][i] = updated_item
            data['data'][i]['lastUpdate'] = datetime.now().isoformat()
            save_data(data)
            return jsonify({"message": "Item updated successfully", "item": data['data'][i]}), 200
    return jsonify({"message": "Item not found"}), 404


@app.route('/api/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    data = load_data()
    data['data'] = [item for item in data['data'] if item['id'] != item_id]
    save_data(data)
    return jsonify({"message": "Item deleted successfully"}), 200


@app.route('/api/bulk_update', methods=['POST'])
def bulk_update():
    update_data = request.json
    data = load_data()
    for item in data['data']:
        if item['id'] in update_data['ids']:
            item['status'] = update_data['status']
            item['lastUpdate'] = datetime.now().isoformat()
    save_data(data)
    return jsonify({"message": "Bulk update successful"}), 200



if __name__ == '__main__':
    app.run(debug=True)