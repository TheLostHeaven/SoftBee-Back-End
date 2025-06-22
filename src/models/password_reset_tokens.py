# src/models/password_reset_token.py
import secrets
from datetime import datetime, timedelta
from .base_model import BaseModel

class PasswordResetTokenModel(BaseModel):
    """Modelo para manejo de tokens de recuperación"""
    
    @staticmethod
    def init_db(db):
        """Inicializa la tabla de tokens"""
        db.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        db.execute('CREATE INDEX IF NOT EXISTS idx_reset_tokens_token ON password_reset_tokens(token)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_reset_tokens_user_id ON password_reset_tokens(user_id)')
        db.commit()

    @staticmethod
    def create_token(db, user_id, expiry_minutes=30):
        """Genera un nuevo token de recuperación"""
        token = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        # Invalidar tokens previos
        PasswordResetTokenModel._execute_update(
            db,
            'UPDATE password_reset_tokens SET used = TRUE WHERE user_id = ?',
            (user_id,)
        )
        
        # Insertar nuevo token
        PasswordResetTokenModel._execute_update(
            db,
            'INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user_id, token, expires_at)
        )
        
        return token

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