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

    @user_bp.route('/login', methods=['POST'])
    def login():
        controller = get_controller()
        data = request.get_json()

        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password required'}), 400

        user = controller.verify_user(data['username'], data['password'])
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        user.pop('password', None)
        user.pop('reset_token', None)
        user.pop('reset_token_expiry', None)
        return jsonify(user), 200

    @user_bp.route('/reset-password', methods=['POST'])
    def request_reset():
        controller = get_controller()

        if 'email' not in request.json:
            return jsonify({'error': 'Email required'}), 400

        token = controller.initiate_password_reset(request.json['email'])
        if not token:
            return jsonify({'error': 'Email not found'}), 404

        return jsonify({'token': token}), 200

    @user_bp.route('/reset-password/<token>', methods=['POST'])
    def reset_password(token):
        controller = get_controller()

        if 'new_password' not in request.json:
            return jsonify({'error': 'New password required'}), 400

        success = controller.reset_password(token, request.json['new_password'])
        if not success:
            return jsonify({'error': 'Invalid or expired token'}), 400

        return jsonify({'message': 'Password updated'}), 200

    return user_bp
