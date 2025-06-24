import psycopg2
import psycopg2.extras

class ApiaryModel:
    @staticmethod
    def init_db(db):
        cursor = db.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS apiaries (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    location VARCHAR(50),   
                    beehives_count INTEGER DEFAULT 0,
                    treatments BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
    def create(db, user_id, name, location=None, beehives_count=0, treatments=False):
        try:
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO apiaries (user_id, name, location, beehives_count, treatments) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (user_id, name, location, beehives_count, treatments)
            )
            apiary_id = cursor.fetchone()[0]
            db.commit()
            return apiary_id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()
    
    @staticmethod
    def get_by_id(db, apiary_id):
        result = ApiaryModel._execute_query(db, 'SELECT * FROM apiaries WHERE id = %s', (apiary_id,))
        return dict(result[0]) if result else None
    
    @staticmethod
    def get_by_user(db, user_id):
        rows = ApiaryModel._execute_query(db, 'SELECT * FROM apiaries WHERE user_id = %s ORDER BY name', (user_id,))
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(db, apiary_id, name=None, location=None):
        fields = []
        params = []
        
        if name is not None:
            fields.append("name = %s")
            params.append(name)
        if location is not None:
            fields.append("location = %s")
            params.append(location)
        
        if not fields:
            raise ValueError("No fields to update")
        
        params.append(apiary_id)
        query = f"UPDATE apiaries SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        ApiaryModel._execute_update(db, query, params)
    
    @staticmethod
    def delete(db, apiary_id):
        ApiaryModel._execute_update(db, 'DELETE FROM apiaries WHERE id = %s', (apiary_id,))
