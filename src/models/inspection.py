class InspectionModel:
    @staticmethod
    def init_db(db):
        cursor = db.cursor()
        try: 
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inspection (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    beehive_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    respuesta TEXT NOT NULL,
                    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (beehive_id) REFERENCES beehive(id) ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE,
                    UNIQUE(beehive_id, question_id, fecha)
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
        """Obtiene todas las inspecciones (datos crudos)"""
        return InspectionModel._execute_query(db, 'SELECT * FROM inspection ORDER BY id')
    
    @staticmethod
    def get_by_id_raw(db, inspection_id):
        """Obtiene una inspección por ID (datos crudos)"""
        return InspectionModel._execute_query(
            db, 
            'SELECT * FROM inspection WHERE id = ?', 
            (inspection_id,)
        )[0] if InspectionModel._execute_query(db, 'SELECT 1 FROM inspection WHERE id = ?', (inspection_id,)) else None
    
    @staticmethod
    def create_raw(db, beehive_id, question_id, respuesta):
        """Crea una nueva inspección (operación cruda)"""
        cursor = InspectionModel._execute_update(
            db,
            'INSERT INTO inspection (beehive_id, question_id, respuesta) '
            'VALUES (?, ?, ?)',
            (beehive_id, question_id, respuesta)
        )
        return cursor.lastrowid

    @staticmethod
    def delete_raw(db, inspection_id):
        """Elimina una pregunta (operación cruda)"""
        InspectionModel._execute_update(
            db,
            'DELETE FROM question WHERE id = ?', 
            (inspection_id,)
        )
        return True
    
    @staticmethod
    def update_raw(db, inspection_id, beehive_id, question_id, respuesta):
        """Actualiza una inspección (operación cruda)"""
        InspectionModel._execute_update(
            db,
            'UPDATE inspection SET beehive_id = ?, question_id = ?, respuesta = ? '
            'WHERE id = ?',
            (beehive_id, question_id, respuesta, inspection_id)
        )
        return True
    
