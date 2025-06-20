from flask import Blueprint, request, jsonify, current_app
from src.models.users import UserModel
from src.database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from src.middleware.jwt import generate_token
import sqlite3

def create_auth_routes():
    auth_bp = Blueprint('auth_routes', __name__)

    # Register
    @auth_bp.route('/register', methods=['POST'])
    def auth_register():
        try:
            data = request.get_json()
            db = get_db()
            
            if UserModel.get_by_username(db, data['username']):
                return jsonify({'error': 'Username already exists'}), 400
            if UserModel.get_by_email(db, data['email']):
                return jsonify({'error': 'Email already exists'}), 400
            
            user_id = UserModel.create(
                db,
                nombre=data['nombre'],
                username=data['username'],
                email=data['email'],
                phone=data['phone'],
                password=generate_password_hash(data['password'])
            )
            
            user_data = UserModel.get_by_id(db, user_id)
            
            token = generate_token(user_id, user_data)
            
            return jsonify({
                'token': token,
                'user_id': user_id,
                'message': 'Registration successful'
            }), 201

        except Exception as err:
            return jsonify({'error': str(err)}), 500

    # Login
    @auth_bp.route('/login', methods=['POST'])
    def auth_login():
        try:
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            data = request.get_json()

            if 'password' not in data:
                return jsonify({
                    'error': 'Password is required',
                    'received': list(data.keys())
                }), 400

            if 'username' not in data and 'email' not in data:
                return jsonify({
                    'error': 'Either username or email is required',
                    'received': list(data.keys())
                }), 400

            db = get_db()
            password = data['password']

            user = None
            if 'username' in data and data['username']:
                user = UserModel.get_by_username(db, data['username'].strip())
            elif 'email' in data and data['email']:
                user = UserModel.get_by_email(db, data['email'].strip())

            if not user:
                return jsonify({
                    'error': 'Invalid credentials',
                    'message': 'User not found with provided credentials'
                }), 401

            if not check_password_hash(user['password'], password):
                return jsonify({
                    'error': 'Invalid credentials',
                    'message': 'Incorrect password'
                }), 401

            token = generate_token(
                user_id=user['id'],
                user_data={
                    'username': user['username'],
                    'email': user['email']
                }
            )

            response_data = {
                'token': token,
                'user_id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'message': 'Login successful'
            }

            return jsonify(response_data), 200

        except sqlite3.Error as db_error:
            current_app.logger.error(f'Database error: {str(db_error)}')
            return jsonify({'error': 'Database operation failed'}), 500
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {str(e)}')
            return jsonify({'error': 'Internal server error'}), 500
    return auth_bp
