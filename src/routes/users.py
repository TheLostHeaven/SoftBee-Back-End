from flask import Blueprint, request, jsonify
from ..controllers.users import UserController
from src.database.db import get_db

def create_user_routes():
    user_bp = Blueprint('user_routes', __name__)

    def get_controller():
        db = get_db()
        return UserController(db)

    @user_bp.route('/users', methods=['POST'])
    def create_user():
        controller = get_controller()
        data = request.get_json()

        required = ['nombre', 'username', 'email', 'phone', 'password']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            user_id = controller.create_user(
                data['nombre'],
                data['username'],
                data['email'],
                data['phone'],
                data['password']
            )
            return jsonify({'id': user_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @user_bp.route('/users', methods=['GET'])
    def get_all_users():
        controller = get_controller()
        try:
            users = controller.get_all_users()
            for user in users:
                user.pop('password', None)
                user.pop('reset_token', None)
                user.pop('reset_token_expiry', None)
            return jsonify(users), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @user_bp.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        controller = get_controller()
        user = controller.get_user(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.pop('password', None)
        user.pop('reset_token', None)
        user.pop('reset_token_expiry', None)
        return jsonify(user), 200

    @user_bp.route('/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        controller = get_controller()
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        try:
            controller.update_user(user_id, **data)
            return jsonify({'message': 'User updated'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @user_bp.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        controller = get_controller()
        try:
            controller.delete_user(user_id)
            return jsonify({'message': 'User deleted'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    return user_bp
