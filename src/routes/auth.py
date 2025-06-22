from flask import Blueprint, request, jsonify, current_app
from src.models.users import UserModel
from src.database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from src.middleware.jwt import generate_token
from src.controllers.auth import AuthController
from src.utils.email_service import EmailService
import sqlite3

def create_auth_routes(get_db_func, email_service):
    auth_bp = Blueprint('auth_routes', __name__)
    
    # Usar get_db_func en lugar de get_db() directamente
    auth_controller = AuthController(db=get_db_func(), mail_service=email_service)

    def clean_user_input(data):
        """Limpia y normaliza los datos de entrada de manera segura"""
        # ... (código existente sin cambios) ...
    
    def get_user_with_profile(user):
        """Añade la URL de la foto de perfil al objeto de usuario"""
        if not user:
            return None
            
        # Limpiar datos sensibles
        user.pop('password', None)
        user.pop('reset_token', None)
        user.pop('reset_token_expiry', None)
        
        # Obtener URL de la foto de perfil
        file_handler = current_app.file_handler
        user['profile_picture_url'] = file_handler.get_profile_picture_url(
            user.get('profile_picture', 'default_profile.jpg')
        )
        
        return user

    # Register
    @auth_bp.route('/register', methods=['POST'])
    def auth_register():
        try:
            data = request.get_json()
            db = get_db_func()  # Obtener conexión al inicio
            
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
                phone=cleaned_data['phone'],
                password=generate_password_hash(cleaned_data['password'])
            )
            
            # Validar creación exitosa
            if not user_id:
                current_app.logger.error('User creation returned invalid ID')
                return jsonify({'error': 'User creation failed'}), 500
            
            # Obtener usuario creado
            user_data = UserModel.get_by_id(db, user_id)
            if not user_data:
                current_app.logger.error(f'User not found after creation, ID: {user_id}')
                return jsonify({'error': 'User retrieval failed'}), 500
                
            # Añadir URL de la foto de perfil
            user_data = get_user_with_profile(user_data)
            
            token = generate_token(user_id, {
                'username': cleaned_data['username'],
                'email': cleaned_data['email'],
                'profile_picture_url': user_data['profile_picture_url']
            })
            
            return jsonify({
                'token': token,
                'user_id': user_id,
                'username': cleaned_data['username'],
                'email': cleaned_data['email'],
                'profile_picture_url': user_data['profile_picture_url'],
                'message': 'Registration successful'
            }), 201

        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except sqlite3.Error as dbe:
            current_app.logger.error(f'Database error: {str(dbe)}')
            return jsonify({'error': 'Database operation failed'}), 500
        except Exception as err:
            current_app.logger.error(f'Unexpected error: {str(err)}', exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500

    # Login
    @auth_bp.route('/login', methods=['POST'])
    def auth_login():
        try:
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            data = request.get_json()
            db = get_db_func()

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

            # Obtener URL de la foto de perfil
            user = get_user_with_profile(user)
            
            # Generar token con foto de perfil
            token = generate_token(
                user_id=user['id'],
                user_data={
                    'username': user['username'],
                    'email': user['email'],
                    'profile_picture_url': user['profile_picture_url']
                }
            )

            return jsonify({
                'token': token,
                'user_id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'profile_picture_url': user['profile_picture_url'],
                'message': 'Login successful'
            }), 200

        except sqlite3.Error as db_error:
            current_app.logger.error(f'Database error: {str(db_error)}')
            return jsonify({'error': 'Database operation failed'}), 500
        except Exception as e:
            current_app.logger.error(f'Unexpected error: {str(e)}')
            return jsonify({'error': 'Internal server error'}), 500
        
    # Forgot Password    
    @auth_bp.route('/forgot-password', methods=['POST'])
    def forgot_password():
        try:
            # Obtener conexión de base de datos
            db = get_db_func()
            
            # Crear controlador con la conexión
            auth_controller = AuthController(db=db, mail_service=email_service)
            
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            
            if not email:
                return jsonify({'error': 'Email is required'}), 400
            
            # Ejecutar operación
            auth_controller.initiate_password_reset(email)
            
            # Obtener usuario para incluir foto en el correo
            user = UserModel.get_by_email(db, email)
            if user:
                # Obtener URL de la foto de perfil
                file_handler = current_app.file_handler
                profile_picture_url = file_handler.get_profile_picture_url(
                    user.get('profile_picture', 'default_profile.jpg')
                )
                
                # Si el servicio de correo admite foto, enviarla
                if hasattr(email_service, 'set_profile_picture_url'):
                    email_service.set_profile_picture_url(profile_picture_url)
            
            db.commit()
            
            return jsonify({
                'message': 'Si el email está registrado, recibirás un correo'
            }), 200
            
        except Exception as e:
            db.rollback()
            current_app.logger.error(f'Error en forgot_password: {str(e)}')
            return jsonify({'error': 'Error al procesar la solicitud'}), 500

    @auth_bp.route('/reset-password', methods=['POST'])
    def reset_password():
        try:
            data = request.get_json()
            token = data.get('token', '').strip()
            new_password = data.get('new_password', '').strip()
            
            if not token or not new_password:
                return jsonify({'error': 'Token y nueva contraseña son requeridos'}), 400
                
            if len(new_password) < 8:
                return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
                
            # Usar el controlador con la conexión actual
            db = get_db_func()
            auth_controller = AuthController(db=db, mail_service=email_service)
            
            if auth_controller.complete_password_reset(token, new_password):
                return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
            else:
                return jsonify({'error': 'Token inválido o expirado'}), 400
        except Exception as e:
            current_app.logger.error(f"Error en reset_password: {str(e)}")
            return jsonify({'error': 'Error interno del servidor'}), 500

    return auth_bp