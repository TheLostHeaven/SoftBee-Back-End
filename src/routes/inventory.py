from flask import Blueprint, request, jsonify
from ..controllers.inventory import InventoryController
from src.database.db import get_db
from src.middleware.jwt import jwt_required

def create_inventory_routes():
    inventory_bp = Blueprint('inventory_routes', __name__)

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory', methods=['POST'])
    @jwt_required
    def create_item(apiary_id):
        db = get_db()
        controller = InventoryController(db)
        data = request.get_json()

        if not data or 'name' not in data:
            return jsonify({'error': 'name is required'}), 400

        try:
            item_id = controller.create_item(
                name=data['name'],
                quantity=data.get('quantity', 0),
                unit=data.get('unit', 'unit'),
                apiary_id=apiary_id 
            )
            return jsonify({'id': item_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @inventory_bp.route('/inventory/<int:item_id>', methods=['GET'])
    @jwt_required
    def get_item(item_id):
        db = get_db()
        controller = InventoryController(db)
        item = controller.get_item(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify(item), 200

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory', methods=['GET'])
    @jwt_required
    def get_apiary_items(apiary_id):
        db = get_db()
        controller = InventoryController(db)
        items = controller.get_apiary_items(apiary_id)
        return jsonify(items), 200
    @inventory_bp.route('/user/inventory', methods=['GET'])
    def get_user_inventory():
        db = get_db()
        controller = InventoryController(db)
        current_user_id =' user_id '


    @inventory_bp.route('/inventory/<int:item_id>', methods=['PUT'])
    @jwt_required
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
    @jwt_required
    def delete_item(item_id):
        db = get_db()
        controller = InventoryController(db)
        try:
            controller.delete_item(item_id)
            return jsonify({'message': 'Item deleted'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory/delete_by_name', methods=['DELETE'])
    @jwt_required
    def delete_by_name(apiary_id):
        db = get_db()
        controller = InventoryController(db)
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'name is required'}), 400

        try:
            controller.delete_by_name(apiary_id, data['name'])
            return jsonify({'message': 'Item(s) deleted'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory/search', methods=['GET'])
    @jwt_required
    def search_items(apiary_id):
        db = get_db()
        controller = InventoryController(db)
        query = request.args.get('query')
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        items = controller.search_items(apiary_id, query)
        return jsonify(items), 200

    @inventory_bp.route('/inventory/<int:item_id>/adjust', methods=['PUT'])
    @jwt_required   
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

    # --- CRUD GENERAL PARA INVENTARIO GENERAL (PROVISIONAL) ---

    @inventory_bp.route('/inventory', methods=['POST'])
    def create_general_item():
        db = get_db()
        data = request.get_json()
        name = data.get('name')
        quantity = data.get('quantity', 0)
        unit = data.get('unit', 'unit')
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        try:
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO inventory (name, quantity, unit) VALUES (%s, %s, %s) RETURNING id',
                (name, quantity, unit)
            )
            item_id = cursor.fetchone()[0]
            db.commit()
            cursor.close()
            return jsonify({'id': item_id, 'message': 'Item created'}), 201
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500

    @inventory_bp.route('/inventory', methods=['GET'])
    def get_all_general_items():
        db = get_db()
        try:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM inventory ORDER BY id')
            columns = [desc[0] for desc in cursor.description]
            items = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return jsonify(items), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @inventory_bp.route('/inventory/<int:item_id>', methods=['GET'])
    def get_general_item(item_id):
        db = get_db()
        try:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM inventory WHERE id = %s', (item_id,))
            row = cursor.fetchone()
            if not row:
                cursor.close()
                return jsonify({'error': 'Item not found'}), 404
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return jsonify(dict(zip(columns, row))), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @inventory_bp.route('/inventory/<int:item_id>', methods=['PUT'])
    def update_general_item(item_id):
        db = get_db()
        data = request.get_json()
        fields = []
        params = []
        for key in ['name', 'quantity', 'unit']:
            if key in data:
                fields.append(f"{key} = %s")
                params.append(data[key])
        if not fields:
            return jsonify({'error': 'No fields to update'}), 400
        params.append(item_id)
        try:
            cursor = db.cursor()
            cursor.execute(
                f'UPDATE inventory SET {", ".join(fields)} WHERE id = %s',
                params
            )
            db.commit()
            if cursor.rowcount == 0:
                cursor.close()
                return jsonify({'error': 'Item not found'}), 404
            cursor.close()
            return jsonify({'message': 'Item updated'}), 200
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500

    @inventory_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
    def delete_general_item(item_id):
        db = get_db()
        try:
            cursor = db.cursor()
            cursor.execute('DELETE FROM inventory WHERE id = %s', (item_id,))
            db.commit()
            if cursor.rowcount == 0:
                cursor.close()
                return jsonify({'error': 'Item not found'}), 404
            cursor.close()
            return jsonify({'message': 'Item deleted'}), 200
        except Exception as e:
            db.rollback()
            return jsonify({'error': str(e)}), 500

    # --- FIN CRUD GENERAL INVENTARIO ---

    return inventory_bp