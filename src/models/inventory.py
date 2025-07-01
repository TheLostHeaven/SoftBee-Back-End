class InventoryModel:
    @staticmethod
    def init_db(db):
        try:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    apiary_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit TEXT NOT NULL DEFAULT 'unit',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_apiary_id ON inventory(apiary_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_item_name ON inventory(item_name)')
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
        return InventoryModel._execute_query(
            db,
            '''SELECT i.* FROM inventory i
               JOIN apiaries a ON i.apiary_id = a.id
               WHERE a.user_id = %s
               ORDER BY i.apiary_id, i.id''',
            (user_id,)
        )

    @staticmethod
    def get_by_apiary(db, apiary_id):
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
    def create(db, apiary_id, item_name, quantity=0, unit='unit'):
        cursor = InventoryModel._execute_update(
            db,
            '''INSERT INTO inventory (apiary_id, item_name, quantity, unit) 
               VALUES (%s, %s, %s, %s) RETURNING id''',
            (apiary_id, item_name, quantity, unit)
        )
        item_id = cursor.fetchone()[0]
        cursor.close()
        return item_id

    @staticmethod
    def update(db, item_id, item_name=None, quantity=None, unit=None):
        fields = []
        params = []

        if item_name is not None:
            fields.append("item_name = %s")
            params.append(item_name)
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
        cursor = InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE id = %s',
            (item_id,)
        )
        cursor.close()

    @staticmethod
    def delete_by_name(db, apiary_id, item_name):
        cursor = InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE apiary_id = %s AND item_name = %s',
            (apiary_id, item_name)
        )
        cursor.close()

    @staticmethod
    def get_by_name(db, apiary_id, item_name):
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE apiary_id = %s AND item_name ILIKE %s',
            (apiary_id, f"%{item_name}%")
        )

    @staticmethod
    def adjust_quantity(db, item_id, amount):
        cursor = InventoryModel._execute_update(
            db,
            '''UPDATE inventory 
               SET quantity = quantity + %s, updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s''',
            (amount, item_id)
        )
        cursor.close()