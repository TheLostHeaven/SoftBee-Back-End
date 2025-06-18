class BeehiveModel:
    @staticmethod
    def init_db(db):
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS beehive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apiary_id INTEGER NOT NULL,
                    queen_year INTEGER,
                    hive_type TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiary(id) ON DELETE CASCADE
                )
            ''')

            db.execute('CREATE INDEX IF NOT EXISTS idx_beehive_apiary ON beehive(apiary_id)')
            db.execute('CREATE INDEX IF NOT EXISTS idx_beehive_queen_year ON beehive(queen_year)')

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
        """Obtiene todas las colmenas (datos crudos)"""
        return BeehiveModel._execute_query(db, 'SELECT * FROM beehive ORDER BY id')

    @staticmethod
    def get_by_id_raw(db, beehive_id):
        """Obtiene una colmena por ID (datos crudos)"""
        return BeehiveModel._execute_query(
            db, 
            'SELECT * FROM beehive WHERE id = ?', 
            (beehive_id,)
        )[0] if BeehiveModel._execute_query(db, 'SELECT 1 FROM beehive WHERE id = ?', (beehive_id,)) else None
        
    @staticmethod
    def create_raw(db, nombre, apiary_id, queen_year=None, hive_type=None):
        """Crea una nueva colmena (operación cruda)"""
        cursor = BeehiveModel._execute_update(
            db,
            'INSERT INTO beehive (nombre, apiary_id, queen_year, hive_type) '
            'VALUES (?, ?, ?, ?)',
            (nombre, apiary_id, queen_year, hive_type)
        )
        return cursor.lastrowid

    @staticmethod
    def update_raw(db, beehive_id, nombre, apiary_id, queen_year=None, hive_type=None):
        """Actualiza una colmena existente (operación cruda)"""
        BeehiveModel._execute_update(
            db,
            'UPDATE beehive SET nombre=?, apiary_id=?, queen_year=?, hive_type=? WHERE id=?',
            (nombre, apiary_id, queen_year, hive_type, beehive_id)
        )
        return True
    
    @staticmethod
    def delete_raw(db, beehive_id):
        """Elimina una colmena por ID (operación cruda)"""
        BeehiveModel._execute_update(
            db, 
            'DELETE FROM beehive WHERE id = ?', 
            (beehive_id,)
        )
        return True

    @staticmethod
    def get_by_apiary_raw(db, apiary_id):
        """Obtiene todas las colmenas de un apiario específico (datos crudos)"""
        return BeehiveModel._execute_query(
            db, 
            'SELECT * FROM beehive WHERE apiary_id = ? ORDER BY nombre', 
            (apiary_id,)
        )
