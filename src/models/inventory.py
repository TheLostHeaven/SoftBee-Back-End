import psycopg2
import psycopg2.extras

class InventoryModel:
    @staticmethod
    def init_db(db):
        cursor = db.cursor()
        try:            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    apiary_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit VARCHAR(50) NOT NULL DEFAULT 'unit',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        return [dict(row) for row in result]

    @staticmethod
    def _execute_single_query(db, query, params=()):
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None

    @staticmethod
    def _execute_update(db, query, params=()):
        cursor = db.cursor()
        cursor.execute(query, params)
        db.commit()
        return cursor

    @staticmethod
    def get_all(db, apiary_id):
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE apiary_id = %s ORDER BY id',
            (apiary_id,)
        )

    @staticmethod
    def get_by_id(db, item_id):
        return InventoryModel._execute_single_query(
            db,
            'SELECT * FROM inventory WHERE id = %s',
            (item_id,)
        )

    @staticmethod
    def create(db, apiary_id, name, quantity=0, unit='unit'):
        query = '''
            INSERT INTO inventory (apiary_id, name, quantity, unit)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        '''
        cursor = db.cursor()
        cursor.execute(query, (apiary_id, name, quantity, unit))
        db.commit()
        item_id = cursor.fetchone()[0]
        cursor.close()
        return item_id

    @staticmethod
    def update(db, item_id, name=None, quantity=None, unit=None):
        fields = []
        params = []
        
        if name is not None:
            fields.append("name = %s")
            params.append(name)
        if quantity is not None:
            fields.append("quantity = %s")
            params.append(quantity)
        if unit is not None:
            fields.append("unit = %s")
            params.append(unit)

        if not fields:
            raise ValueError("No fields to update")

        params.append(item_id)
        query = f"UPDATE inventory SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        InventoryModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, item_id):
        InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE id = %s',
            (item_id,)
        )

    @staticmethod
    def delete_by_name(db, apiary_id, name):
        InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE apiary_id = %s AND name = %s',
            (apiary_id, name)
        )

    @staticmethod
    def get_by_name(db, apiary_id, name):
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE apiary_id = %s AND name LIKE %s',
            (apiary_id, f"%{name}%")
        )

    @staticmethod
    def adjust_quantity(db, item_id, amount):
        InventoryModel._execute_update(
            db,
            'UPDATE inventory SET quantity = quantity + %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            (amount, item_id)
        )

    @staticmethod
    def get_by_user_id(db, user_id):
        """Obtiene todos los items de inventario de todos los apiarios de un usuario"""
        return InventoryModel._execute_query(
            db,
            '''SELECT i.* FROM inventory i
            JOIN apiaries a ON i.apiary_id = a.id
            WHERE a.user_id = %s''',
            (user_id,)
        )
