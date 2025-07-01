import sqlite3

class ApiaryModel:
    @staticmethod
    def init_db(db):
        cursor = db.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS apiaries (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    location TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_apiaries_user_id ON apiaries(user_id)')
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            raise e
    
    @staticmethod
    def _execute_query(db, query, params=()):
        return db.execute(query, params).fetchall()
    
    @staticmethod
    def _execute_update(db, query, params=()):
        cursor = db.execute(query, params)
        db.commit()
        return cursor
    
    @staticmethod
    def create(db, user_id, name, location=None):
        cursor = ApiaryModel._execute_update(
            db,
            'INSERT INTO apiaries (user_id, name, location) VALUES (?, ?, ?)',
            (user_id, name, location))
        return cursor.lastrowid
    
    @staticmethod
    def get_by_id(db, apiary_id):
        result = ApiaryModel._execute_query(db, 'SELECT * FROM apiaries WHERE id = ?', (apiary_id,))
        return dict(result[0]) if result else None
    
    @staticmethod
    def get_by_user(db, user_id):
        rows = ApiaryModel._execute_query(db, 'SELECT * FROM apiaries WHERE user_id = ? ORDER BY name', (user_id,))
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(db, apiary_id, name=None, location=None):
        fields = []
        params = []
        
        if name is not None:
            fields.append("name = ?")
            params.append(name)
        if location is not None:
            fields.append("location = ?")
            params.append(location)
        
        if not fields:
            raise ValueError("No fields to update")
        
        params.append(apiary_id)
        query = f"UPDATE apiaries SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        ApiaryModel._execute_update(db, query, params)
    
    @staticmethod
    def delete(db, apiary_id):
        ApiaryModel._execute_update(db, 'DELETE FROM apiaries WHERE id = ?', (apiary_id,))
