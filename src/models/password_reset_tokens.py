import secrets
from datetime import datetime, timedelta

class PasswordResetTokenModel:
    """Modelo para manejo de tokens de recuperación en PostgreSQL"""
    
    @staticmethod
    def init_db(db):
        """Inicializa la tabla de tokens en PostgreSQL"""
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
            
            # Crear índices para mejor rendimiento
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token 
                ON password_reset_tokens (token)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id 
                ON password_reset_tokens (user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expiry 
                ON password_reset_tokens (expires_at)
            ''')
            
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def create_token(db, user_id, expires_minutes=30):
        """Genera un nuevo token de recuperación para PostgreSQL"""
        cursor = db.cursor()
        try:
            token = secrets.token_urlsafe(64)
            expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
            
            # Invalidar tokens previos del mismo usuario
            cursor.execute(
                "UPDATE password_reset_tokens SET used = TRUE WHERE user_id = %s AND used = FALSE",
                (user_id,)
            )
            
            # Insertar nuevo token y obtener el ID creado
            cursor.execute(
                "INSERT INTO password_reset_tokens (user_id, token, expires_at) "
                "VALUES (%s, %s, %s) RETURNING token",
                (user_id, token, expires_at)
            )
            
            created_token = cursor.fetchone()[0]
            db.commit()
            return created_token
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error creando token: {str(e)}")
        finally:
            cursor.close()

    @staticmethod
    def validate_token(db, token):
        """Valida un token de recuperación en PostgreSQL"""
        cursor = db.cursor()
        try:
            cursor.execute(
                """
                SELECT user_id 
                FROM password_reset_tokens 
                WHERE token = %s 
                AND expires_at > CURRENT_TIMESTAMP 
                AND used = FALSE
                """,
                (token,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            raise RuntimeError(f"Error validando token: {str(e)}")
        finally:
            cursor.close()

    @staticmethod
    def mark_as_used(db, token):
        """Marca un token como utilizado en PostgreSQL"""
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s",
                (token,)
            )
            db.commit()
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Error marcando token como usado: {str(e)}")
        finally:
            cursor.close()