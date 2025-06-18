class QuestionModel:
    @staticmethod
    def init_db(db):
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS question (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pregunta TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    min INTEGER,
                    max INTEGER,
                    obligatorio BOOLEAN NOT NULL DEFAULT 0,
                    opciones TEXT,
                    id_externo TEXT UNIQUE 
                )
            ''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_question_tipo ON question(tipo)')
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
        """Obtiene todas las preguntas (datos crudos)"""
        return QuestionModel._execute_query(db, 'SELECT * FROM question ORDER BY id')

    @staticmethod
    def get_by_id_raw(db, question_id):
        """Obtiene una pregunta por ID (datos crudos)"""
        return QuestionModel._execute_query(
            db, 
            'SELECT * FROM question WHERE id = ?', 
            (question_id,)
        )[0] if QuestionModel._execute_query(db, 'SELECT 1 FROM question WHERE id = ?', (question_id,)) else None

    @staticmethod
    def create_raw(db, pregunta, tipo, obligatorio, min=None, max=None, opciones=None):
        """Crea una nueva pregunta (operación cruda)"""
        cursor = QuestionModel._execute_update(
            db,
            'INSERT INTO question (pregunta, tipo, min, max, obligatorio, opciones) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (pregunta, tipo, min, max, 1 if obligatorio else 0, 
            ','.join(opciones) if opciones else None)
        )
        return cursor.lastrowid

    @staticmethod
    def update_raw(db, question_id, **kwargs):
        """Actualiza una pregunta (operación cruda)"""
        allowed_fields = {'pregunta', 'tipo', 'min', 'max', 'obligatorio', 'opciones'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
            
        set_clause = ', '.join(f"{k} = ?" for k in updates)
        values = list(updates.values())
        values.append(question_id)
        
        QuestionModel._execute_update(
            db,
            f'UPDATE question SET {set_clause} WHERE id = ?',
            values
        )
        return True

    @staticmethod
    def delete_raw(db, question_id):
        """Elimina una pregunta (operación cruda)"""
        QuestionModel._execute_update(
            db,
            'DELETE FROM question WHERE id = ?', 
            (question_id,)
        )
        return True

    @staticmethod
    def get_by_type_raw(db, tipo):
        """Obtiene preguntas por tipo (datos crudos)"""
        return QuestionModel._execute_query(
            db,
            'SELECT * FROM question WHERE tipo = ? ORDER BY pregunta',
            (tipo,)
        )