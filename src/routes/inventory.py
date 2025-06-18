from flask import Blueprint, request, jsonify
from src.controllers.inventory import InventoryController

# Blueprint con prefijo /api/inventory
inventory_bp = Blueprint('inventory_routes', __name__, url_prefix='/api/inventory')

@inventory_bp.route('/', methods=['GET'])
def get_all_items():
    """Obtiene todos los items del inventario"""
    response, status_code = InventoryController.get_all_items()
    return jsonify(response), status_code

@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Obtiene un item específico por ID"""
    response, status_code = InventoryController.get_item(item_id)
    return jsonify(response), status_code

@inventory_bp.route('/', methods=['POST'])
def create_item():
    """Crea un nuevo item en el inventario"""
    data = request.get_json()
    response, status_code = InventoryController.create_item(data)
    return jsonify(response), status_code

@inventory_bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Actualiza un item existente"""
    data = request.get_json()
    response, status_code = InventoryController.update_item(item_id, data)
    return jsonify(response), status_code

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Elimina un item del inventario"""
    response, status_code = InventoryController.delete_item(item_id)
    return jsonify(response), status_code

@inventory_bp.route('/search', methods=['GET'])
def search_items():
    """Busca items por nombre"""
    item_name = request.args.get('name')
    response, status_code = InventoryController.search_items(item_name)
    return jsonify(response), status_code