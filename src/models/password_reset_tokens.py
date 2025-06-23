# src/models/password_reset_token.py
import secrets
from datetime import datetime, timedelta
from .base_model import BaseModel

class PasswordResetTokenModel(BaseModel):
    """Modelo para manejo de tokens de recuperación"""
    
    @staticmethod
    def _get_placeholder(db):
        """Determina el marcador de posición según el motor de BD"""
        driver = str(db.__class__).lower()
        return '%s' if 'psycopg' in driver or 'postgres' in driver else '?'

    @staticmethod
    def _get_timestamp_function(db):
        """Determina la función para obtener el timestamp actual"""
        driver = str(db.__class__).lower()
        return 'CURRENT_TIMESTAMP' if 'psycopg' in driver or 'postgres' in driver else "datetime('now')"

    @staticmethod
    def init_db(db):
        """Inicializa la tabla de tokens"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    used BOOLEAN DEFAULT FALSE,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def create_token(db, user_id, expires_minutes=30):
        """Genera un nuevo token de recuperación"""
        cursor = None
        try:
            placeholder = PasswordResetTokenModel._get_placeholder(db)
            token = secrets.token_urlsafe(64)
            expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
            
            cursor = db.cursor()
            
            # Invalidar tokens previos (compatible con PostgreSQL y SQLite)
            invalidate_query = f"""
                UPDATE password_reset_tokens 
                SET used = TRUE 
                WHERE user_id = {placeholder} 
                AND used = FALSE
            """
            cursor.execute(invalidate_query, (user_id,))
            
            # Insertar nuevo token
            insert_query = f"""
                INSERT INTO password_reset_tokens 
                (user_id, token, expires_at) 
                VALUES ({placeholder}, {placeholder}, {placeholder})
            """
            cursor.execute(insert_query, (user_id, token, expires_at))
            
            db.commit()
            return token
        
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error creating token: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def validate_token(db, token):
        """Valida un token de recuperación"""
        cursor = None
        try:
            placeholder = PasswordResetTokenModel._get_placeholder(db)
            timestamp_func = PasswordResetTokenModel._get_timestamp_function(db)
            
            query = f"""
                SELECT user_id FROM password_reset_tokens 
                WHERE token = {placeholder} 
                AND expires_at > {timestamp_func} 
                AND used = FALSE
            """
            cursor = db.cursor()
            cursor.execute(query, (token,))
            result = cursor.fetchone()
            
            return result['user_id'] if result else None
        except Exception as e:
            raise RuntimeError(f"Error validating token: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def mark_as_used(db, token):
        """Marca un token como utilizado"""
        cursor = None
        try:
            placeholder = PasswordResetTokenModel._get_placeholder(db)
            query = f"""
                UPDATE password_reset_tokens 
                SET used = TRUE 
                WHERE token = {placeholder}
            """
            cursor = db.cursor()
            cursor.execute(query, (token,))
            db.commit()
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error marking token as used: {str(e)}")
        finally:
            if cursor:
                cursor.close()