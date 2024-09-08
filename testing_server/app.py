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

@app.route('/api/data', methods=['POST'])
def handle_data():
    if not request.json or 'action' not in request.json:
        return jsonify({"error": "Invalid request format"}), 400

    action = request.json['action']

    if action == 'get':
        # 保持现有的 GET 逻辑不变
        data = load_data()
        filtered_data = filter_sort_paginate(data['data'], request.json)
        return jsonify(filtered_data)
    elif action == 'delete':
        # 新增删除功能
        if 'id' not in request.json:
            return jsonify({"error": "No id provided for deletion"}), 400
        item_id = request.json['id']
        data = load_data()
        data['data'] = [item for item in data['data'] if item['id'] != item_id]
        save_data(data)
        return jsonify({"message": "Item deleted successfully"}), 200
    else:
        return jsonify({"error": "Invalid action"}), 400

def filter_sort_paginate(data, params):
    # Apply filtering
    if 'filter' in params:
        data = [item for item in data if apply_filter(item, params['filter'])]

    # Apply sorting
    if 'sort' in params:
        reverse = params['sort']['order'] == 'desc'
        data.sort(key=lambda x: x[params['sort']['field']], reverse=reverse)

    # Calculate pagination
    page = int(params.get('page', 1))
    items_per_page = int(params.get('itemsPerPage', 10))
    total_items = len(data)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # Apply pagination
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_data = data[start:end]

    return {
        'data': paginated_data,
        'totalItems': total_items,
        'totalPages': total_pages,
        'currentPage': page
    }

def apply_filter(item, filter_params):
    for key, value in filter_params.items():
        if key == 'status' and value and item['status'] != value:
            return False
        if key == 'minAmount' and value and float(item['amount'].replace('$', '').replace(',', '')) < float(value):
            return False
        if key == 'maxAmount' and value and float(item['amount'].replace('$', '').replace(',', '')) > float(value):
            return False
    return True
@app.route('/api/summary', methods=['POST'])
def get_summary():
    data = load_data()
    all_data = data['data']  # 使用所有数据，不应用过滤器

    total_amount = 0
    total_count = len(all_data)
    active_amount = 0
    inactive_amount = 0
    active_count = 0
    inactive_count = 0

    for item in all_data:
        amount = float(item['amount'].replace('$', '').replace(',', ''))
        total_amount += amount
        if item['status'] == 'Active':
            active_amount += amount
            active_count += 1
        elif item['status'] == 'Inactive':
            inactive_amount += amount
            inactive_count += 1

    summary = {
        'totalAmount': round(total_amount, 2),
        'totalCount': total_count,
        'activeAmount': round(active_amount, 2),
        'inactiveAmount': round(inactive_amount, 2),
        'activeCount': active_count,
        'inactiveCount': inactive_count
    }

    return jsonify(summary)
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