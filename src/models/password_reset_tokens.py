# src/models/password_reset_token.py
import secrets
from datetime import datetime, timedelta
from .base_model import BaseModel

class PasswordResetTokenModel(BaseModel):
    """Modelo para manejo de tokens de recuperación"""
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
                    expires_at DATETIME NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
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
        try:
            token = secrets.token_urlsafe(64)
            expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
            
            cursor = db.cursor()
            
            # Invalidar tokens previos
            cursor.execute(
                'UPDATE password_reset_tokens SET used = 1 WHERE user_id = ? AND used = 0',
                (user_id,)
            )
            
            # Insertar nuevo token
            cursor.execute(
                'INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
                (user_id, token, expires_at)
            )
            
            db.commit()
            return token
        
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error creating token: {str(e)}")
        finally:
            # Cerrar el cursor explícitamente
            if cursor:
                cursor.close()

    @staticmethod
    def validate_token(db, token):
        """Valida un token de recuperación"""
        result = PasswordResetTokenModel._execute_query(
            db,
            '''
            SELECT user_id FROM password_reset_tokens 
            WHERE token = ? 
            AND expires_at > datetime('now') 
            AND used = FALSE
            ''',
            (token,)
        )
        return result[0]['user_id'] if result else None

    @staticmethod
    def mark_as_used(db, token):
        """Marca un token como utilizado"""
        PasswordResetTokenModel._execute_update(
            db,
            'UPDATE password_reset_tokens SET used = TRUE WHERE token = ?',
            (token,)
        )