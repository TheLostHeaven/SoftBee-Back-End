from flask import Blueprint, request, jsonify, g
from ..controllers.inventory import InventoryController
from ..controllers.apiary import ApiaryController
from src.database.db import get_db
from src.middleware.jwt import jwt_required

def create_inventory_routes():
    inventory_bp = Blueprint('inventory_routes', __name__)

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory', methods=['POST'])
    @jwt_required
    def create_item(apiary_id):
        db = get_db()
        inventory_controller = InventoryController(db)
        apiary_controller = ApiaryController(db)
        user_id = g.current_user_id
        
        # Verificar que el usuario es propietario del apiario
        apiary = apiary_controller.get_by_id(apiary_id)
        if not apiary or apiary['user_id'] != user_id:
            return jsonify({'error': 'Apiario no encontrado o acceso denegado'}), 404

        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'El nombre es requerido'}), 400

        try:
            item_id = inventory_controller.create_item(
                apiary_id=apiary_id,
                name=data['name'],
                quantity=data.get('quantity', 0),
                unit=data.get('unit', 'unit'),
                description=data.get('description'),
                minimum_stock=data.get('minimum_stock', 0)
            )
            return jsonify({'id': item_id, 'message': 'Item creado exitosamente'}), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Error al crear item: {str(e)}'}), 500

    @inventory_bp.route('/inventory/<int:item_id>', methods=['GET'])
    @jwt_required
    def get_item(item_id):
        db = get_db()
        controller = InventoryController(db)
        user_id = g.current_user_id
        
        # Verificar acceso del usuario al item
        if not controller.validate_user_access(item_id, user_id):
            return jsonify({'error': 'Item no encontrado o acceso denegado'}), 404
            
        item = controller.get_item_with_apiary(item_id)
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
            
        return jsonify(item), 200

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory', methods=['GET'])
    @jwt_required
    def get_apiary_items(apiary_id):
        db = get_db()
        inventory_controller = InventoryController(db)
        apiary_controller = ApiaryController(db)
        user_id = g.current_user_id
        
        # Verificar que el usuario es propietario del apiario
        apiary = apiary_controller.get_by_id(apiary_id)
        if not apiary or apiary['user_id'] != user_id:
            return jsonify({'error': 'Apiario no encontrado o acceso denegado'}), 404

        items = inventory_controller.get_apiary_items(apiary_id)
        return jsonify(items), 200

    @inventory_bp.route('/user/inventory', methods=['GET'])
    @jwt_required
    def get_user_inventory():
        db = get_db()
        controller = InventoryController(db)
        user_id = g.current_user_id
        items = controller.get_user_inventory(user_id)
        return jsonify(items), 200

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory/summary', methods=['GET'])
    @jwt_required
    def get_apiary_summary(apiary_id):
        db = get_db()
        inventory_controller = InventoryController(db)
        apiary_controller = ApiaryController(db)
        user_id = g.current_user_id
        
        # Verificar que el usuario es propietario del apiario
        apiary = apiary_controller.get_by_id(apiary_id)
        if not apiary or apiary['user_id'] != user_id:
            return jsonify({'error': 'Apiario no encontrado o acceso denegado'}), 404

        summary = inventory_controller.get_apiary_summary(apiary_id)
        return jsonify(summary), 200

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory/low-stock', methods=['GET'])
    @jwt_required
    def get_low_stock_items(apiary_id):
        db = get_db()
        inventory_controller = InventoryController(db)
        apiary_controller = ApiaryController(db)
        user_id = g.current_user_id
        
        # Verificar que el usuario es propietario del apiario
        apiary = apiary_controller.get_by_id(apiary_id)
        if not apiary or apiary['user_id'] != user_id:
            return jsonify({'error': 'Apiario no encontrado o acceso denegado'}), 404

        items = inventory_controller.get_low_stock_items(apiary_id)
        return jsonify(items), 200


    @inventory_bp.route('/inventory/<int:item_id>', methods=['PUT'])
    @jwt_required
    def update_item(item_id):
        db = get_db()
        controller = InventoryController(db)
        user_id = g.current_user_id
        
        # Verificar acceso del usuario al item
        if not controller.validate_user_access(item_id, user_id):
            return jsonify({'error': 'Item no encontrado o acceso denegado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400

        try:
            controller.update_item(item_id, **data)
            return jsonify({'message': 'Item actualizado exitosamente'}), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'Error al actualizar item: {str(e)}'}), 500

    @inventory_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
    @jwt_required
    def delete_item(item_id):
        db = get_db()
        controller = InventoryController(db)
        user_id = g.current_user_id
        
        # Verificar acceso del usuario al item
        if not controller.validate_user_access(item_id, user_id):
            return jsonify({'error': 'Item no encontrado o acceso denegado'}), 404
        
        try:
            controller.delete_item(item_id)
            return jsonify({'message': 'Item eliminado exitosamente'}), 200
        except Exception as e:
            return jsonify({'error': f'Error al eliminar item: {str(e)}'}), 500

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory/delete_by_name', methods=['DELETE'])
    @jwt_required
    def delete_by_name(apiary_id):
        db = get_db()
        inventory_controller = InventoryController(db)
        apiary_controller = ApiaryController(db)
        user_id = g.current_user_id
        
        # Verificar que el usuario es propietario del apiario
        apiary = apiary_controller.get_by_id(apiary_id)
        if not apiary or apiary['user_id'] != user_id:
            return jsonify({'error': 'Apiario no encontrado o acceso denegado'}), 404

        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'El nombre es requerido'}), 400

        try:
            inventory_controller.delete_by_name(apiary_id, data['name'])
            return jsonify({'message': 'Item(s) eliminado(s) exitosamente'}), 200
        except Exception as e:
            return jsonify({'error': f'Error al eliminar item(s): {str(e)}'}), 500

    @inventory_bp.route('/apiaries/<int:apiary_id>/inventory/search', methods=['GET'])
    @jwt_required
    def search_items(apiary_id):
        db = get_db()
        inventory_controller = InventoryController(db)
        apiary_controller = ApiaryController(db)
        user_id = g.current_user_id
        
        # Verificar que el usuario es propietario del apiario
        apiary = apiary_controller.get_by_id(apiary_id)
        if not apiary or apiary['user_id'] != user_id:
            return jsonify({'error': 'Apiario no encontrado o acceso denegado'}), 404

        query = request.args.get('query')
        if not query:
            return jsonify({'error': 'Parámetro de búsqueda requerido'}), 400
            
        items = inventory_controller.search_items(apiary_id, query)
        return jsonify(items), 200

    @inventory_bp.route('/inventory/<int:item_id>/adjust', methods=['PUT'])
    @jwt_required   
    def adjust_quantity(item_id):
        db = get_db()
        controller = InventoryController(db)
        user_id = g.current_user_id
        
        # Verificar acceso del usuario al item
        if not controller.validate_user_access(item_id, user_id):
            return jsonify({'error': 'Item no encontrado o acceso denegado'}), 404
        
        data = request.get_json()
        if not data or 'amount' not in data:
            return jsonify({'error': 'La cantidad es requerida'}), 400

        try:
            amount = int(data['amount'])
            controller.adjust_quantity(item_id, amount)
            return jsonify({'message': 'Cantidad ajustada exitosamente'}), 200
        except ValueError:
            return jsonify({'error': 'La cantidad debe ser un número entero'}), 400
        except Exception as e:
            return jsonify({'error': f'Error al ajustar cantidad: {str(e)}'}), 500

    return inventory_bp
