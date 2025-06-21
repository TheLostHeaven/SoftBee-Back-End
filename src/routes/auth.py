from flask import Blueprint, request, jsonify, current_app
from src.models.users import UserModel
from src.database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from src.middleware.jwt import generate_token
import sqlite3

def create_auth_routes():
    auth_bp = Blueprint('auth_routes', __name__)

    def clean_user_input(data):
        """Limpia los espacios en blanco de los inputs y valida campos requeridos"""
        cleaned = {
            'nombre': data.get('nombre', '').strip(),
            'username': data.get('username', '').strip().lower(),  # Normaliza a minúsculas
            'email': data.get('email', '').strip().lower(),
            'phone': data.get('phone', '').strip(),
            'password': data.get('password', '').strip()
        }
        
        # Validación de campos requeridos
        if not cleaned['username']:
            raise ValueError('Username is required')
        if not cleaned['password']:
            raise ValueError('Password is required')
        if not cleaned['email']:
            raise ValueError('Email is required')
            
        return cleaned

    # Register
    @auth_bp.route('/register', methods=['POST'])
    def auth_register():
        try:
            data = request.get_json()
            db = get_db()
            
            # Limpia y valida los datos
            cleaned_data = clean_user_input(data)
            
            # Validaciones adicionales
            if len(cleaned_data['password']) < 8:
                return jsonify({'error': 'Password must be at least 8 characters'}), 400
                
            if UserModel.get_by_username(db, cleaned_data['username']):
                return jsonify({'error': 'Username already exists'}), 400
                
            if UserModel.get_by_email(db, cleaned_data['email']):
                return jsonify({'error': 'Email already exists'}), 400
            
            # Crear usuario con datos limpios
            user_id = UserModel.create(
                db,
                nombre=cleaned_data['nombre'],
                username=cleaned_data['username'],
                email=cleaned_data['email'],
                phone=cleaned_data['phone'],  # Ahora es string garantizado
                password=generate_password_hash(cleaned_data['password'])
            )
            
            user_data = UserModel.get_by_id(db, user_id)
            token = generate_token(user_id, user_data)
            
            return jsonify({
                'token': token,
                'user_id': user_id,
                'username': cleaned_data['username'],
                'email': cleaned_data['email'],
                'message': 'Registration successful'
            }), 201

        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except sqlite3.Error as dbe:
            current_app.logger.error(f'Database error: {str(dbe)}')
            return jsonify({'error': 'Database operation failed'}), 500
        except Exception as err:
            current_app.logger.error(f'Unexpected error: {str(err)}')
            return jsonify({'error': 'Internal server error'}), 500

    # Login
    @auth_bp.route('/login', methods=['POST'])
    def auth_login():
        try:
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            data = request.get_json()
            db = get_db()

            # Limpieza y validación básica
            identifier = data.get('username', data.get('email', '')).strip().lower()
            password = data.get('password', '').strip()

            if not password:
                return jsonify({'error': 'Password is required'}), 400
                
            if not identifier:
                return jsonify({'error': 'Username or email is required'}), 400

            # Buscar usuario por username o email (ya normalizados)
            user = None
            if '@' in identifier:
                user = UserModel.get_by_email(db, identifier)
            else:
                user = UserModel.get_by_username(db, identifier)

            if not user:
                current_app.logger.warning(f'Login attempt for non-existent user: {identifier}')
                return jsonify({
                    'error': 'Invalid credentials',
                    'message': 'User not found with provided credentials'
                }), 401

            if not check_password_hash(user['password'], password):
                current_app.logger.warning(f'Failed login attempt for user: {user["username"]}')
                return jsonify({
                    'error': 'Invalid credentials',
                    'message': 'Incorrect password'
                }), 401

            # Generar token
            token = generate_token(
                user_id=user['id'],
                user_data={
                    'username': user['username'],
                    'email': user['email']
                }
            )

            return jsonify({
                'token': token,
                'user_id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'message': 'Login successful'
            }), 200

        except sqlite3.Error as db_error:
            current_app.logger.error(f'Database error: {str(db_error)}')
            return jsonify({'error': 'Database operation failed'}), 500
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {str(e)}')
            return jsonify({'error': 'Internal server error'}), 500

    return auth_bp