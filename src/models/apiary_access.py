class ApiaryAccessModel:
    @staticmethod
    def init_db(db):
        cursor= db.cursor()
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS apiary_access (
                user_id INTEGER NOT NULL,
                apiary_id INTEGER NOT NULL,
                permission_level INTEGER DEFAULT 1, 
                PRIMARY KEY (user_id, apiary_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (apiary_id) REFERENCES apiary(id) ON DELETE CASCADE
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
        """Ejecuta una consulta y retorna resultados"""
        return db.execute(query, params).fetchall()
    
    @staticmethod
    def _execute_update(db, query, params=()):
        """Ejecuta una actualización y hace commit"""
        cursor = db.execute(query, params)
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
            'SELECT * FROM apiary_access WHERE user_id = ? ORDER BY apiary_id', 
            (user_id,)
        )
    
    @staticmethod
    def get_by_apiary_id_raw(db, apiary_id):
        """Obtiene todos los accesos a un apiario específico (datos crudos)"""
        return ApiaryAccessModel._execute_query(
            db, 
            'SELECT * FROM apiary_access WHERE apiary_id = ? ORDER BY user_id', 
            (apiary_id,)
        )
    
    @staticmethod
    def create_raw(db, user_id, apiary_id, permission_level=1):
        """Crea un nuevo acceso a un apiario (operación cruda)"""
        cursor = ApiaryAccessModel._execute_update(
            db,
            'INSERT INTO apiary_access (user_id, apiary_id, permission_level) '
            'VALUES (?, ?, ?)',
            (user_id, apiary_id, permission_level)
        )
        return cursor.lastrowid
    
    @staticmethod
    def update_raw(db, user_id, apiary_id, permission_level):
        """Actualiza el nivel de acceso a un apiario existente (operación cruda)"""
        cursor = ApiaryAccessModel._execute_update(
            db,
            'UPDATE apiary_access SET permission_level = ? WHERE user_id = ? AND apiary_id = ?',
            (permission_level, user_id, apiary_id)
        )
        return cursor.rowcount > 0
    
    @staticmethod
    def delete_raw(db, user_id, apiary_id):
        """Elimina un acceso a un apiario por usuario y apiario (operación cruda)"""
        cursor = ApiaryAccessModel._execute_update(
            db, 
            'DELETE FROM apiary_access WHERE user_id = ? AND apiary_id = ?', 
            (user_id, apiary_id)
        )
        return cursor.rowcount > 0
    
