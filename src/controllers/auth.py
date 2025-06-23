# src/controllers/auth_controller.py
from src.models.users import UserModel
from flask import current_app,request, jsonify
from src.models.password_reset_tokens import PasswordResetTokenModel
import sqlite3
import src.middleware.jwt as generate_token
import bcrypt

class AuthController:
    def __init__(self, db, mail_service=None):
        self.db = db
        self.mail_service = mail_service
        
    def register_user(self, nombre, username, email, phone, password):
        """Registra un nuevo usuario"""
        # Verifica si el usuario ya existe
        if UserModel.get_by_email(self.db, email):
            raise ValueError("El email ya está registrado")
        if UserModel.get_by_username(self.db, username):
            raise ValueError("El nombre de usuario ya existe")
            
        # Crea el usuario con contraseña hasheada usando bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return UserModel.create(
            self.db,
            nombre=nombre,
            username=username,
            email=email,
            phone=phone,
            password=hashed_password
        )
    
    def authenticate_user(self, identifier, password):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email y contraseña requeridos"}), 400

        user = UserModel.query.filter_by(email=email).first()
        
        if not user:
            current_app.logger.warning(f"Intento de login con email no registrado: {email}")
            return jsonify({"error": "Credenciales inválidas"}), 401

        if not user.check_password(password):
            current_app.logger.warning(f"Intento de login con contraseña incorrecta para: {email}")
            return jsonify({"error": "Credenciales inválidas"}), 401

        auth_token = generate_token(user.id)
        return jsonify({
            "message": "Login exitoso",
            "token": auth_token,
            "user_id": user.id
        }), 200
        
    def initiate_password_reset(self, email):
        """Inicia el proceso de recuperación de contraseña"""
        try:
            # Validación del email
            if not email or not isinstance(email, str):
                raise ValueError("Email inválido")
            
            email = email.strip().lower()
            
            # Buscar usuario
            user = UserModel.get_by_email(self.db, email)
            if not user:
                current_app.logger.info(f"Intento de reset para email no registrado: {email}")
                return None
                
            expires_minutes = current_app.config.get('EXPIRES_TOKEN_EMAIL', 15)
            
            # Convertir a entero si es necesario
            if isinstance(expires_minutes, str):
                try:
                    expires_minutes = int(expires_minutes)
                except ValueError:
                    expires_minutes = 15
                    
            # Generar token
            token = PasswordResetTokenModel.create_token(
                self.db, 
                user['id'],
                expires_minutes=expires_minutes
            )

            
            # Enviar correo
            if self.mail_service:
                reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
                self.mail_service.send_password_reset(
                    email=email,
                    token=token,
                    reset_url=reset_url
                )
            
            return token
            
        except sqlite3.Error as db_error:
            self.db.rollback()
            current_app.logger.error(f"Error de base de datos: {str(db_error)}")
            raise
        except Exception as e:
            current_app.logger.error(f"Error inesperado: {str(e)}")
            raise
    
    def complete_password_reset(self, token, new_password):
        """Completa el proceso de recuperación de contraseña"""
        # Valida el token
        user_id = PasswordResetTokenModel.validate_token(self.db, token)
        if not user_id:
            return False
            
        # Actualiza la contraseña usando bcrypt
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        UserModel.update_password(self.db, user_id, hashed_password)
        
        # Marca el token como usado
        PasswordResetTokenModel.mark_as_used(self.db, token)
        
        return True
    
    def get_user_by_id(self, user_id):
        """Obtiene un usuario por su ID"""
        return UserModel.get_by_id(self.db, user_id)