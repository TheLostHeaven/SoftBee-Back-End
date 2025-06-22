# src/controllers/auth_controller.py
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.users import UserModel
from flask import current_app
from src.models.password_reset_tokens import PasswordResetTokenModel
from config import front_end_url


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
            
        # Crea el usuario con contraseña hasheada
        hashed_password = generate_password_hash(password)
        return UserModel.create(
            self.db,
            nombre=nombre,
            username=username,
            email=email,
            phone=phone,
            password=hashed_password
        )
    
    def authenticate_user(self, identifier, password):
        """Autentica un usuario por email o username"""
        user = None
        if '@' in identifier:
            user = UserModel.get_by_email(self.db, identifier)
        else:
            user = UserModel.get_by_username(self.db, identifier)
            
        if user and check_password_hash(user['password'], password):
            return user
        return None
        
    def initiate_password_reset(self, email):
        """Inicia el proceso de recuperación de contraseña"""
        user = UserModel.get_by_email(self.db, email)
        if not user:
            # Por seguridad, no revelamos si el email existe
            return None
            
        # Genera token seguro
        token = PasswordResetTokenModel.create_token(self.db, user['id'])
        
        # Envía el correo electrónico (si hay servicio configurado)
        if self.mail_service:
            reset_url = f"{current_app.config.get(front_end_url, '')}/reset-password?token={token}"
            self.mail_service.send_password_reset(email, token, reset_url)
        
        return token
    
    def complete_password_reset(self, token, new_password):
        """Completa el proceso de recuperación de contraseña"""
        # Valida el token
        user_id = PasswordResetTokenModel.validate_token(self.db, token)
        if not user_id:
            return False
            
        # Actualiza la contraseña
        hashed_password = generate_password_hash(new_password)
        UserModel.update_password(self.db, user_id, hashed_password)
        
        # Marca el token como usado
        PasswordResetTokenModel.mark_as_used(self.db, token)
        
        return True
    
    def get_user_by_id(self, user_id):
        """Obtiene un usuario por su ID"""
        return UserModel.get_by_id(self.db, user_id)