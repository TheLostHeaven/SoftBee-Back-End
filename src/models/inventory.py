class ApiaryModel:
    @staticmethod
    def init_db(db):
        try:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS apiaries (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_apiaries_user_id ON apiaries(user_id)')
            db.commit()
            cursor.close()
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def _execute_query(db, query, params=()):
        cursor = db.cursor()
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results

    @staticmethod
    def _execute_single_query(db, query, params=()):
        cursor = db.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        result = None
        if row:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row))
        cursor.close()
        return result

    @staticmethod
    def _execute_update(db, query, params=()):
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()
        return cursor

    @staticmethod
    def get_by_user(db, user_id):
        return ApiaryModel._execute_query(
            db,
            'SELECT * FROM apiaries WHERE user_id = %s ORDER BY id',
            (user_id,)
        )

    @staticmethod
    def get_by_id(db, apiary_id):
        return ApiaryModel._execute_single_query(
            db,
            'SELECT * FROM apiaries WHERE id = %s',
            (apiary_id,)
        )

    @staticmethod
    def create(db, user_id, name, location=None):
        cursor = ApiaryModel._execute_update(
            db,
            '''INSERT INTO apiaries (user_id, name, location)
               VALUES (%s, %s, %s) RETURNING id''',
            (user_id, name, location)
        )
        apiary_id = cursor.fetchone()[0]
        cursor.close()
        return apiary_id

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
        cursor = ApiaryModel._execute_update(
            db,
            'DELETE FROM apiaries WHERE id = %s',
            (apiary_id,)
        )
        cursor.close()
