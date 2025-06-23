# src/models/user.py
import os
from werkzeug.security import generate_password_hash, check_password_hash
from .base_model import BaseModel
from datetime import datetime, timedelta
from flask import current_app

class UserModel(BaseModel):
    @staticmethod
    def init_db(db):
        cursor = db.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    password VARCHAR(200) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    # ======================== MÉTODOS COMPATIBLES ========================
    @staticmethod
    def _execute_query(db, query, params=()):
        """Ejecuta consultas con cursores explícitos"""
        cursor = db.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convertir a diccionarios
        if results:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in results]
        return []

    @staticmethod
    def _execute_update(db, query, params=()):
        """Ejecuta actualizaciones con cursores explícitos"""
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()
        return cursor

    @staticmethod
    def create(db, nombre, username, email, phone, password):
        is_postgres = 'postgres' in os.environ.get('DATABASE_URL', '').lower()
        hashed_password = generate_password_hash(password)
        current_app.logger.debug(f"Hashed password: {hashed_password}") 

        if is_postgres:
            cursor = db.cursor()
            cursor.execute(
                '''
                INSERT INTO users (nombre, username, email, phone, password)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                ''',
                (nombre, username.lower(), email.lower(), phone, hashed_password)
            )
            user_id = cursor.fetchone()[0]
            db.commit()
            return user_id
        else:
            cursor = UserModel._execute_update(
                db,
                '''
                INSERT INTO users (nombre, username, email, phone, password)
                VALUES (%s, %s, %s, %s, %s)
                ''',
                (nombre, username.lower(), email.lower(), phone, generate_password_hash(password))
            )
            return cursor.lastrowid

    @staticmethod
    def get_by_id(db, user_id):
        """Obtiene usuario por ID (compatible)"""
        result = UserModel._execute_query(
            db,
            'SELECT * FROM users WHERE id = %s',
            (user_id,)
        )
        return result[0] if result else None

    @staticmethod
    def get_by_username(db, username):
        """Obtiene usuario por username (compatible)"""
        result = UserModel._execute_query(
            db,
            'SELECT * FROM users WHERE username = %s',
            (username,)
        )
        return result[0] if result else None

    @staticmethod
    def get_by_email(db, email):
        """Obtiene usuario por email (compatible)"""
        result = UserModel._execute_query(
            db,
            'SELECT * FROM users WHERE email = %s',
            (email.lower(),)
        )
        return result[0] if result else None

    @staticmethod
    def verify_password(db, user_id, password):
        """Verifica contraseña (compatible)"""
        user = UserModel.get_by_id(db, user_id)
        return user and check_password_hash(user['password'], password)

    @staticmethod
    def update(db, user_id, **kwargs):
        """Actualiza usuario (compatible)"""
        fields = []
        params = []
        valid_keys = ['nombre', 'username', 'email', 'phone', 'password', 'profile_picture']
        
        for key in valid_keys:
            if key in kwargs and kwargs[key] is not None:
                fields.append(f"{key} = %s")
                params.append(kwargs[key] if key != 'password' else generate_password_hash(kwargs[key]))
        
        if not fields:
            raise ValueError("No fields provided to update")
        
        params.append(user_id)
        query = f'''
            UPDATE users
            SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        '''
        UserModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, user_id):
        """Elimina usuario (compatible)"""
        UserModel._execute_update(db, 'DELETE FROM users WHERE id = %s', (user_id,))

    @staticmethod
    def set_reset_token(db, email, token, expiry_hours=1):
        """Establece token de reseteo (compatible)"""
        expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        UserModel._execute_update(
            db,
            'UPDATE users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s',
            (token, expiry, email.lower())
        )

    @staticmethod
    def verify_reset_token(db, token):
        """Verifica token de reseteo (compatible)"""
        result = UserModel._execute_query(
            db,
            '''
            SELECT * FROM users 
            WHERE reset_token = %s 
            AND reset_token_expiry > CURRENT_TIMESTAMP
            ''',
            (token,)
        )
        return result[0] if result else None

    @staticmethod
    def update_password(db, user_id, new_password_hash):
        """Actualiza el hash de contraseña de un usuario"""
        try:
            cursor = db.cursor()
            placeholder = '?' if 'sqlite' in str(type(db)) else '%s'
            cursor.execute(
                f"UPDATE users SET password = {placeholder} WHERE id = {placeholder}",
                (new_password_hash, user_id))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error actualizando contraseña: {str(e)}")
            return False

    @staticmethod
    def update_profile_picture(db, user_id, filename):
        """Actualiza foto de perfil (compatible)"""
        UserModel._execute_update(
            db,
            'UPDATE users SET profile_picture = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            (filename, user_id)
        )

    @staticmethod
    def get_all(db):
        """Obtiene todos los usuarios (compatible)"""
        return UserModel._execute_query(db, 'SELECT * FROM users ORDER BY id')