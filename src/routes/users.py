from flask import Blueprint, request, jsonify, current_app, g
from ..controllers.users import UserController
from src.database.db import get_db
from src.middleware.jwt import jwt_required
from src.models.apiary import ApiaryModel

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
                data['password'],
                data.get('profile_picture')
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

        # Limpiar campos sensibles
        user.pop('password', None)
        user.pop('reset_token', None)
        user.pop('reset_token_expiry', None)
        
        # Añadir URL de la foto de perfil
        file_handler = current_app.file_handler
        user['profile_picture_url'] = file_handler.get_profile_picture_url(
            user.get('profile_picture', 'default_profile.jpg')
        )

        # Añadir apiarios asociados al usuario
        user['apiaries'] = ApiaryModel.get_by_user(get_db(), user_id)

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

    # Endpoint para actualizar foto de perfil
    @user_bp.route('/users/<int:user_id>/profile-picture', methods=['PUT'])
    @jwt_required
    def update_profile_picture(user_id):
        if g.current_user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        file_handler = current_app.file_handler
        filename = file_handler.save_profile_picture(file, user_id)

        if not filename:
            return jsonify({'error': 'Invalid file type'}), 400

        controller = get_controller()
        controller.update_profile_picture(user_id, filename)

        return jsonify({
            'profile_picture': file_handler.get_profile_picture_url(filename)
        }), 200

    @user_bp.route('/users/me', methods=['GET'])
    @jwt_required
    def get_me():
        controller = get_controller()
        user_id = g.current_user_id
        user = controller.get_user(user_id)

        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        user.pop('password', None)
        user.pop('reset_token', None)
        user.pop('reset_token_expiry', None)

        file_handler = current_app.file_handler
        user['profile_picture_url'] = file_handler.get_profile_picture_url(
            user.get('profile_picture', 'default_profile.jpg')
        )

        user['apiaries'] = ApiaryModel.get_by_user(get_db(), user_id)

        return jsonify(user), 200

    return user_bp
