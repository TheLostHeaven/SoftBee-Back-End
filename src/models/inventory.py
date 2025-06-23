import sqlite3

class InventoryModel:
    @staticmethod
    def init_db(db):
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apiary_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit TEXT NOT NULL DEFAULT 'unit',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
                )
            ''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_inventory_apiary_id ON inventory(apiary_id)')
            db.execute('CREATE INDEX IF NOT EXISTS idx_inventory_item_name ON inventory(item_name)')
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            raise e

    @staticmethod
    def _execute_query(db, query, params=()):
        cursor = db.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def _execute_single_query(db, query, params=()):
        cursor = db.execute(query, params)
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))
        return None

    @staticmethod
    def _execute_update(db, query, params=()):
        cursor = db.execute(query, params)
        db.commit()
        return cursor

    @staticmethod
    def get_all(db, apiary_id):
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE apiary_id = ? ORDER BY id',
            (apiary_id,)
        )

    @staticmethod
    def get_by_id(db, item_id):
        return InventoryModel._execute_single_query(
            db,
            'SELECT * FROM inventory WHERE id = ?',
            (item_id,)
        )

    @staticmethod
    def create(db, apiary_id, item_name, quantity=0, unit='unit'):
        cursor = InventoryModel._execute_update(
            db,
            'INSERT INTO inventory (apiary_id, item_name, quantity, unit) VALUES (?, ?, ?, ?)',
            (apiary_id, item_name, quantity, unit)
        )
        return cursor.lastrowid

    @staticmethod
    def update(db, item_id, item_name=None, quantity=None, unit=None):
        fields = []
        params = []

        if item_name is not None:
            fields.append("item_name = ?")
            params.append(item_name)
        if quantity is not None:
            fields.append("quantity = ?")
            params.append(quantity)
        if unit is not None:
            fields.append("unit = ?")
            params.append(unit)

        if not fields:
            raise ValueError("No fields to update")

        params.append(item_id)
        query = f"UPDATE inventory SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        InventoryModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, item_id):
        InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE id = ?',
            (item_id,)
        )

    @staticmethod
    def delete_by_name(db, apiary_id, item_name):
        InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE apiary_id = ? AND item_name = ?',
            (apiary_id, item_name)
        )

    @staticmethod
    def get_by_name(db, apiary_id, item_name):
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE apiary_id = ? AND item_name LIKE ?',
            (apiary_id, f"%{item_name}%")
        )

    @staticmethod
    def adjust_quantity(db, item_id, amount):
        InventoryModel._execute_update(
            db,
            'UPDATE inventory SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (amount, item_id)
        )

    @staticmethod
    def get_by_user_id(db, user_id):
        """Obtiene todos los items de inventario de todos los apiarios de un usuario"""
        return InventoryModel._execute_query(
            db,
            '''SELECT i.* FROM inventory i
               JOIN apiaries a ON i.apiary_id = a.id
               WHERE a.user_id = ?''',
            (user_id,)
        )