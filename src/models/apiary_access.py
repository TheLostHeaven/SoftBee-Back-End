import psycopg2
import psycopg2.extras

class ApiaryAccessModel:
    @staticmethod
    def init_db(db):
        cursor = db.cursor()
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS apiary_access (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                apiary_id INTEGER NOT NULL,
                permission_level INTEGER DEFAULT 1, 
                PRIMARY KEY (user_id, apiary_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
            )
            ''')

            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
        
    @staticmethod
    def _execute_query(db, query, params=()):
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    @staticmethod
    def _execute_update(db, query, params=()):
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()
        return cursor
    
    @staticmethod
    def get_all_raw(db):
        """Obtiene todos los accesos a apiarios (datos crudos)"""
        return ApiaryAccessModel._execute_query(db, 'SELECT * FROM apiary_access ORDER BY user_id, apiary_id')

    @staticmethod
    def get_by_user_id_raw(db, user_id):
        """Obtiene todos los accesos de un usuario específico (datos crudos)"""
        return ApiaryAccessModel._execute_query(
            db, 
            'SELECT * FROM apiary_access WHERE user_id = %s ORDER BY apiary_id', 
            (user_id,)
        )
    
    @staticmethod
    def get_by_apiary_id_raw(db, apiary_id):
        """Obtiene todos los accesos a un apiario específico (datos crudos)"""
        return ApiaryAccessModel._execute_query(
            db, 
            'SELECT * FROM apiary_access WHERE apiary_id = %s ORDER BY user_id', 
            (apiary_id,)
        )
    
    @staticmethod
    def create_raw(db, user_id, apiary_id, permission_level=1):
        """Crea un nuevo acceso a un apiario (operación cruda)"""
        cursor = ApiaryAccessModel._execute_update(
            db,
            'INSERT INTO apiary_access (user_id, apiary_id, permission_level) VALUES (%s, %s, %s) RETURNING user_id',
            (user_id, apiary_id, permission_level)
        )
        inserted_id = cursor.fetchone()[0]
        cursor.close()
        return inserted_id
    
    @staticmethod
    def update_raw(db, user_id, apiary_id, permission_level):
        """Actualiza el nivel de acceso a un apiario existente (operación cruda)"""
        cursor = ApiaryAccessModel._execute_update(
            db,
            'UPDATE apiary_access SET permission_level = %s WHERE user_id = %s AND apiary_id = %s',
            (permission_level, user_id, apiary_id)
        )
        updated = cursor.rowcount > 0
        cursor.close()
        return updated
    
    @staticmethod
    def delete_raw(db, user_id, apiary_id):
        """Elimina un acceso a un apiario por usuario y apiario (operación cruda)"""
        cursor = ApiaryAccessModel._execute_update(
            db, 
            'DELETE FROM apiary_access WHERE user_id = %s AND apiary_id = %s', 
            (user_id, apiary_id)
        )
        deleted = cursor.rowcount > 0
        cursor.close()
        return deleted

