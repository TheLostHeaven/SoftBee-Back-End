import psycopg2
import psycopg2.extras

class BeehiveModel:
    @staticmethod
    def init_db(db):
        cursor = db.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS beehives (
                    id SERIAL PRIMARY KEY,
                    apiary_id INTEGER NOT NULL,
                    hive_number INTEGER NOT NULL,
                    activity_level TEXT CHECK(activity_level IN ('Baja', 'Media', 'Alta')),
                    bee_population TEXT CHECK(bee_population IN ('Baja', 'Media', 'Alta')),
                    food_frames INTEGER,
                    brood_frames INTEGER,
                    hive_status TEXT CHECK(hive_status IN (
                        'Cámara de cría',
                        'Cámara de cría y producción',
                        'Cámara de cría y doble alza de producción'
                    )),
                    health_status TEXT CHECK(health_status IN (
                        'Presencia barroa',
                        'Presencia de polilla',
                        'Presencia de curruncho',
                        'Mortalidad- malformación en nodrizas',
                        'Ninguno'
                    )),
                    has_production_chamber TEXT CHECK(has_production_chamber IN ('Si', 'No')),
                    observations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE,
                    UNIQUE(apiary_id, hive_number)
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
    def create(db, apiary_id, hive_number, **kwargs):
        fields = ['apiary_id', 'hive_number']
        values = [apiary_id, hive_number]
        placeholders = ['%s', '%s']

        for field, value in kwargs.items():
            if value is not None:
                fields.append(field)
                values.append(value)
                placeholders.append('%s')

        query = f"INSERT INTO hives ({', '.join(fields)}) VALUES ({', '.join(placeholders)}) RETURNING id"
        cursor = BeehiveModel._execute_update(db, query, values)
        hive_id = cursor.fetchone()[0]
        cursor.close()
        return hive_id

    @staticmethod
    def get_by_id(db, hive_id):
        result = BeehiveModel._execute_query(db, 'SELECT * FROM hives WHERE id = %s', (hive_id,))
        return dict(result[0]) if result else None

    @staticmethod
    def get_by_apiary(db, apiary_id):
        result = BeehiveModel._execute_query(db, 'SELECT * FROM hives WHERE apiary_id = %s ORDER BY hive_number', (apiary_id,))
        return [dict(row) for row in result]

    @staticmethod
    def update(db, hive_id, **kwargs):
        if not kwargs:
            raise ValueError("No fields to update")

        fields = []
        params = []
        for field, value in kwargs.items():
            fields.append(f"{field} = %s")
            params.append(value)

        params.append(hive_id)
        query = f"UPDATE hives SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        BeehiveModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, hive_id):
        BeehiveModel._execute_update(db, 'DELETE FROM hives WHERE id = %s', (hive_id,))

    @staticmethod
    def get_hive_number(db, apiary_id, hive_number):
        result = BeehiveModel._execute_query(
            db,
            'SELECT * FROM hives WHERE apiary_id = %s AND hive_number = %s',
            (apiary_id, hive_number))
        return dict(result[0]) if result else None
