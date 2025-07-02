from flask import Blueprint, request, jsonify
from .controllers.beehive import HiveController
from src.database.db import get_db

def create_hive_routes():
    hive_bp = Blueprint('hive_routes', __name__)

    @hive_bp.route('/apiaries/<int:apiary_id>/hives', methods=['POST'])
    def create_hive(apiary_id):
        db = get_db()
        controller = HiveController(db)

        data = request.get_json()
        if 'hive_number' not in data:
            return jsonify({'error': 'Hive number required'}), 400

        if not isinstance(data['hive_number'], int):
            return jsonify({'error': 'Hive number must be integer'}), 400

        try:
            hive_id = controller.create_hive(
                apiary_id,
                data['hive_number'],
                **{k: v for k, v in data.items() if k != 'hive_number'}
            )
            return jsonify({'id': hive_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @hive_bp.route('/hives/<int:hive_id>', methods=['GET'])
    def get_hive(hive_id):
        db = get_db()
        controller = HiveController(db)

        hive = controller.get_hive(hive_id)
        if not hive:
            return jsonify({'error': 'Hive not found'}), 404
        return jsonify(hive), 200

    @hive_bp.route('/apiaries/<int:apiary_id>/hives', methods=['GET'])
    def get_apiary_hives(apiary_id):
        db = get_db()
        controller = HiveController(db)

        hives = controller.get_apiary_hives(apiary_id)
        return jsonify(hives), 200

    @hive_bp.route('/hives/<int:hive_id>', methods=['PUT'])
    def update_hive(hive_id):
        db = get_db()
        controller = HiveController(db)

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        try:
            controller.update_hive(hive_id, **data)
            return jsonify({'message': 'Hive updated'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @hive_bp.route('/hives/<int:hive_id>', methods=['DELETE'])
    def delete_hive(hive_id):
        db = get_db()
        controller = HiveController(db)

        try:
            controller.delete_hive(hive_id)
            return jsonify({'message': 'Hive deleted'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @hive_bp.route('/apiaries/<int:apiary_id>/hives/number/<int:hive_number>', methods=['GET'])
    def get_hive_by_number(apiary_id, hive_number):
        db = get_db()
        controller = HiveController(db)

        hive = controller.get_hive_by_number(apiary_id, hive_number)
        if not hive:
            return jsonify({'error': 'Hive not found'}), 404
        return jsonify(hive), 200

    return hive_bp
