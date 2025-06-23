import bcrypt
from datetime import datetime, timedelta
from flask import current_app

class UserModel:
    @staticmethod
    def init_db(db):
        """Inicializa la tabla de usuarios en PostgreSQL"""
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices para mejor rendimiento
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)
            ''')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def _execute_query(db, query, params=()):
        """Ejecuta consultas y retorna resultados como diccionarios"""
        cursor = db.cursor()
        try:
            cursor.execute(query, params)
            # Convertir resultados a diccionarios
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            return []
        except Exception as e:
            current_app.logger.error(f"Error en consulta: {str(e)}")
            raise e
        finally:
            cursor.close()

    @staticmethod
    def _execute_update(db, query, params=()):
        """Ejecuta actualizaciones y hace commit"""
        cursor = db.cursor()
        try:
            cursor.execute(query, params)
            db.commit()
            return cursor
        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error en actualización: {str(e)}")
            raise e
        finally:
            cursor.close()

    @staticmethod
    def create(db, nombre, username, email, phone, password):
        """Crea un nuevo usuario en PostgreSQL. Recibe el hash ya generado."""
        current_app.logger.debug(f"Hashed password: {password}") 
        cursor = db.cursor()
        try:
            cursor.execute(
                '''
                INSERT INTO users (nombre, username, email, phone, password)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                ''',
                (nombre, username.lower(), email.lower(), phone, password)
            )
            user_id = cursor.fetchone()[0]
            db.commit()
            return user_id
        except Exception as e:
            db.rollback()
            current_app.logger.error(f"Error creando usuario: {str(e)}")
            raise e
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(db, user_id):
        """Obtiene usuario por ID"""
        results = UserModel._execute_query(
            db,
            'SELECT * FROM users WHERE id = %s',
            (user_id,)
        )
        return results[0] if results else None

    @staticmethod
    def get_by_username(db, username):
        """Obtiene usuario por username"""
        results = UserModel._execute_query(
            db,
            'SELECT * FROM users WHERE username = %s',
            (username,)
        )
        return results[0] if results else None

    @staticmethod
    def get_by_email(db, email):
        """Obtiene usuario por email"""
        results = UserModel._execute_query(
            db,
            'SELECT * FROM users WHERE email = %s',
            (email.lower(),)
        )
        return results[0] if results else None

    @staticmethod
    def verify_password(db, user_id, password):
        """Verifica contraseña usando bcrypt"""
        user = UserModel.get_by_id(db, user_id)
        if not user:
            return False
        stored_password = user['password']
        if stored_password and (stored_password.startswith('$2b$') or stored_password.startswith('$2a$')):
            return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        return False

    @staticmethod
    def update(db, user_id, **kwargs):
        """Actualiza usuario en PostgreSQL"""
        if not kwargs:
            raise ValueError("No fields provided to update")
        
        # Campos permitidos para actualizar
        valid_keys = ['nombre', 'username', 'email', 'phone', 'password']
        
        # Preparar campos y valores
        set_clause = []
        params = []
        
        for key, value in kwargs.items():
            if key in valid_keys and value is not None:
                # Solo aceptar el hash ya generado para password
                set_clause.append(f"{key} = %s")
                params.append(value)
        
        if not set_clause:
            raise ValueError("No valid fields to update")
        
        # Agregar user_id al final de los parámetros
        params.append(user_id)
        
        query = f'''
            UPDATE users
            SET {', '.join(set_clause)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        '''
        
        UserModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, user_id):
        """Elimina usuario"""
        UserModel._execute_update(
            db, 
            'DELETE FROM users WHERE id = %s', 
            (user_id,)
        )

    @staticmethod
    def set_reset_token(db, email, token, expiry_hours=1):
        """Establece token de reseteo"""
        expiry = datetime.utcnow() + timedelta(hours=expiry_hours)
        UserModel._execute_update(
            db,
            '''
            UPDATE users 
            SET reset_token = %s, reset_token_expiry = %s 
            WHERE email = %s
            ''',
            (token, expiry, email.lower())
        )

    @staticmethod
    def verify_reset_token(db, token):
        """Verifica token de reseteo"""
        results = UserModel._execute_query(
            db,
            '''
            SELECT * FROM users 
            WHERE reset_token = %s 
            AND reset_token_expiry > CURRENT_TIMESTAMP
            ''',
            (token,)
        )
        return results[0] if results else None

    @staticmethod
    def update_password(db, user_id, new_password):
        """Actualiza la contraseña de un usuario. Recibe el hash ya generado."""
        UserModel._execute_update(
            db,
            'UPDATE users SET password = %s WHERE id = %s',
            (new_password, user_id)
        )
        return True

    @staticmethod
    def update_profile_picture(db, user_id, filename):
        """Actualiza foto de perfil"""
        UserModel._execute_update(
            db,
            '''
            UPDATE users 
            SET profile_picture = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
            ''',
            (filename, user_id)
        )

    @staticmethod
    def get_all(db):
        """Obtiene todos los usuarios"""
        return UserModel._execute_query(
            db, 
            'SELECT * FROM users ORDER BY id'
        )