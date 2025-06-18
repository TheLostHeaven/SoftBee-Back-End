class ApiaryModel:
    @staticmethod
    def init_db(db):
        try:
            db.execute('''
            CREATE TABLE IF NOT EXISTS apiary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user INTEGER NOT NULL,
                nombre_apiario TEXT NOT NULL,
                direccion TEXT NOT NULL,
                cantidad_colmenas INTEGER NOT NULL,
                latitud REAL NOT NULL,
                longitud REAL NOT NULL,
                aplica_tratamiento BOOLEAN NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_apiary_user ON apiary(id_user)')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        
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
        """Obtiene todos los apiarios (datos crudos)"""
        return ApiaryModel._execute_query(db, 'SELECT * FROM apiary ORDER BY id')

    @staticmethod
    def get_by_id_raw(db, apiary_id):
        """Obtiene un apiario por ID (datos crudos)"""
        return ApiaryModel._execute_query(
            db, 
            'SELECT * FROM apiary WHERE id = ?', 
            (apiary_id,)
        )[0] if ApiaryModel._execute_query(db, 'SELECT 1 FROM apiary WHERE id = ?', (apiary_id,)) else None
    
    @staticmethod
    def create_raw(db, id_user, nombre_apiario, direccion, cantidad_colmenas, latitud, longitud, aplica_tratamiento=False):
        """Crea un nuevo apiario (operación cruda)"""
        cursor = ApiaryModel._execute_update(
            db,
            'INSERT INTO apiary (id_user, nombre_apiario, direccion, cantidad_colmenas, latitud, longitud, aplica_tratamiento) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (id_user, nombre_apiario, direccion, cantidad_colmenas, latitud, longitud, aplica_tratamiento)
        )
        return cursor.lastrowid
    
    @staticmethod
    def update_raw(db, apiary_id, id_user, nombre_apiario, direccion, cantidad_colmenas, latitud, longitud, aplica_tratamiento=False):
        """Actualiza un apiario existente (operación cruda)"""
        cursor = ApiaryModel._execute_update(
            db,
            '''
            UPDATE apiary 
            SET id_user=?, nombre_apiario=?, direccion=?, cantidad_colmenas=?, latitud=?, longitud=?, aplica_tratamiento=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            ''',
            (id_user, nombre_apiario, direccion, cantidad_colmenas, latitud, longitud, aplica_tratamiento, apiary_id)
        )
        return cursor.rowcount > 0
    
    @staticmethod
    def delete_raw(db, apiary_id):
        """Elimina un apiario existente (operación cruda)"""
        cursor = ApiaryModel._execute_update(
            db,
            'DELETE FROM apiary WHERE id = ?',
            (apiary_id,)
        )
        return cursor.rowcount > 0
    
    @staticmethod
    def get_by_user_raw(db, user_id):
        """Obtiene todos los apiarios de un usuario específico (datos crudos)"""
        return ApiaryModel._execute_query(
            db, 
            'SELECT * FROM apiary WHERE id_user = ? ORDER BY nombre_apiario', 
            (user_id,)
        )