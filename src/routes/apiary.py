from flask import Blueprint, request, jsonify
from ..controllers.apiary import ApiaryController
from src.database.db import get_db

def create_apiary_routes():
    apiary_bp = Blueprint('apiary_routes', __name__)

    @apiary_bp.route('/apiaries', methods=['GET'])
    def get_all_apiaries():
        db = get_db()
        controller = ApiaryController(db)
        try:
            apiaries = controller.get_all_apiaries()
            return jsonify(apiaries), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @apiary_bp.route('/apiaries', methods=['POST'])
    def create_apiary():
        db = get_db()
        controller = ApiaryController(db)
        data = request.get_json()
        if 'user_id' not in data or 'name' not in data:
            return jsonify({'error': 'User ID and name are required'}), 400
        try:
            apiary_id = controller.create_apiary(
                data['user_id'],
                data['name'],
                data.get('location')
            )
            return jsonify({'id': apiary_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @apiary_bp.route('/apiaries/<int:apiary_id>', methods=['GET'])
    def get_apiary(apiary_id):
        db = get_db()
        controller = ApiaryController(db)
        try:
            apiary = controller.get_apiary(apiary_id)
            if not apiary:
                return jsonify({'error': 'Apiary not found'}), 404
            return jsonify(apiary), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @apiary_bp.route('/users/<int:user_id>/apiaries', methods=['GET'])
    def get_user_apiaries(user_id):
        db = get_db()
        controller = ApiaryController(db)
        try:
            apiaries = controller.get_user_apiaries(user_id)
            return jsonify(apiaries), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @apiary_bp.route('/apiaries/<int:apiary_id>', methods=['PUT'])
    def update_apiary(apiary_id):
        db = get_db()
        controller = ApiaryController(db)
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        try:
            updated = controller.update_apiary(apiary_id, **data)
            if not updated:
                return jsonify({'error': 'Apiary not found or not updated'}), 404
            return jsonify({'message': 'Apiary updated successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @apiary_bp.route('/apiaries/<int:apiary_id>', methods=['DELETE'])
    def delete_apiary(apiary_id):
        db = get_db()
        controller = ApiaryController(db)
        try:
            deleted = controller.delete_apiary(apiary_id)
            if not deleted:
                return jsonify({'error': 'Apiary not found or not deleted'}), 404
            return jsonify({'message': 'Apiary deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return apiary_bp
