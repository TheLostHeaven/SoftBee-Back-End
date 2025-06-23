from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..controllers.inventory import InventoryController
from src.database.db import get_db

def create_inventory_routes():
    inventory_bp = Blueprint('inventory_routes', __name__)

    @inventory_bp.route('/inventory', methods=['POST'])
    @jwt_required()
    def create_item():
        db = get_db()
        controller = InventoryController(db)
        data = request.get_json()

        if not data or 'apiary_id' not in data or 'item_name' not in data:
            return jsonify({'error': 'apiary_id and item_name are required'}), 400

        try:
            item_id = controller.create_item(
                data['apiary_id'],
                data['item_name'],
                data.get('quantity', 0),
                data.get('unit', 'unit')
            )
            return jsonify({'id': item_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @inventory_bp.route('/inventory/<int:item_id>', methods=['GET'])
    @jwt_required()
    def get_item(item_id):
        db = get_db()
        controller = InventoryController(db)
        item = controller.get_item(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify(item), 200

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory', methods=['GET'])
    @jwt_required()
    def get_apiary_items(apiary_id):
        db = get_db()
        controller = InventoryController(db)
        items = controller.get_apiary_items(apiary_id)
        return jsonify(items), 200

    @inventory_bp.route('/user/inventory', methods=['GET'])
    @jwt_required()
    def get_user_inventory():
        db = get_db()
        controller = InventoryController(db)
        current_user_id = get_jwt_identity()

        try:
            items = controller.get_user_inventory(current_user_id)
            return jsonify(items), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @inventory_bp.route('/inventory/<int:item_id>', methods=['PUT'])
    @jwt_required()
    def update_item(item_id):
        db = get_db()
        controller = InventoryController(db)
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        try:
            controller.update_item(item_id, **data)
            return jsonify({'message': 'Item updated'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @inventory_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
    @jwt_required()
    def delete_item(item_id):
        db = get_db()
        controller = InventoryController(db)
        try:
            controller.delete_item(item_id)
            return jsonify({'message': 'Item deleted'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory/delete_by_name', methods=['DELETE'])
    @jwt_required()
    def delete_by_name(apiary_id):
        db = get_db()
        controller = InventoryController(db)
        data = request.get_json()
        if not data or 'item_name' not in data:
            return jsonify({'error': 'item_name is required'}), 400

        try:
            controller.delete_by_name(apiary_id, data['item_name'])
            return jsonify({'message': 'Item(s) deleted'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory/search', methods=['GET'])
    @jwt_required()
    def search_items(apiary_id):
        db = get_db()
        controller = InventoryController(db)
        query = request.args.get('query')
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        items = controller.search_items(apiary_id, query)
        return jsonify(items), 200

    @inventory_bp.route('/inventory/<int:item_id>/adjust', methods=['PUT'])
    @jwt_required()
    def adjust_quantity(item_id):
        db = get_db()
        controller = InventoryController(db)
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({'error': 'Amount is required'}), 400

        try:
            amount = int(data['amount'])
            controller.adjust_quantity(item_id, amount)
            return jsonify({'message': 'Quantity adjusted'}), 200
        except ValueError:
            return jsonify({'error': 'Amount must be an integer'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    return inventory_bp