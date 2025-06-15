def init(db):
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


class Question:
    @staticmethod
    def get_all(db, grupo=None):
        query = 'SELECT * FROM question'
        params = ()
        
        if grupo:
            query += ' WHERE grupo = ?'
            params = (grupo,)
            
        query += ' ORDER BY id'
        return db.execute(query, params).fetchall()
    
    @staticmethod
    def get_by_id(db, question_id):
        return db.execute(
            'SELECT * FROM question WHERE id = ?', 
            (question_id,)
        ).fetchone()
    
    @staticmethod
    def create(db, pregunta, tipo, obligatorio, grupo, min_val=None, max_val=None, opciones=None):
        cursor = db.execute(
            'INSERT INTO question (pregunta, tipo, min_val, max_val, obligatorio, opciones, grupo) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (pregunta, tipo, min_val, max_val, 1 if obligatorio else 0, 
            ','.join(opciones) if opciones else None, grupo)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update(db, question_id, **kwargs):
        allowed_fields = {'pregunta', 'tipo', 'min_val', 'max_val', 'obligatorio', 'opciones', 'grupo'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
            
        set_clause = ', '.join(f"{k} = ?" for k in updates)
        values = list(updates.values())
        values.append(question_id)
        
        db.execute(
            f'UPDATE question SET {set_clause} WHERE id = ?',
            values
        )
        db.commit()
        return True
    
    @staticmethod
    def delete(db, question_id):
        db.execute('DELETE FROM question WHERE id = ?', (question_id,))
        db.commit()
        return True
    
    @staticmethod
    def get_by_type(db, tipo):
        return db.execute(
            'SELECT * FROM question WHERE tipo = ? ORDER BY pregunta',
            (tipo,)
        ).fetchall()