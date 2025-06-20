import sqlite3

class InventoryModel:
    @staticmethod
    def init_db(db):
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit TEXT NOT NULL DEFAULT 'unit',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_inventory_user_id ON inventory(user_id)')
            db.execute('CREATE INDEX IF NOT EXISTS idx_inventory_item_name ON inventory(item_name)')
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            raise e

    @staticmethod
    def _execute_query(db, query, params=()):
        """Executes a query and returns results as list of dicts"""
        cursor = db.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def _execute_single_query(db, query, params=()):
        """Executes a query and returns a single result as dict"""
        cursor = db.execute(query, params)
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))
        return None

    @staticmethod
    def _execute_update(db, query, params=()):
        """Executes an update and commits"""
        cursor = db.execute(query, params)
        db.commit()
        return cursor

    @staticmethod
    def get_all(db, user_id):
        """Gets all inventory items for a user"""
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE user_id = ? ORDER BY id',
            (user_id,)
        )

    @staticmethod
    def get_by_id(db, item_id):
        """Gets an inventory item by ID"""
        return InventoryModel._execute_single_query(
            db,
            'SELECT * FROM inventory WHERE id = ?',
            (item_id,)
        )

    @staticmethod
    def create(db, user_id, item_name, quantity=0, unit='unit'):
        """Creates a new inventory item"""
        cursor = InventoryModel._execute_update(
            db,
            'INSERT INTO inventory (user_id, item_name, quantity, unit) VALUES (?, ?, ?, ?)',
            (user_id, item_name, quantity, unit)
        )
        return cursor.lastrowid

    @staticmethod
    def update(db, item_id, item_name=None, quantity=None, unit=None):
        """Updates an existing inventory item"""
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
        """Deletes an inventory item"""
        InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE id = ?',
            (item_id,)
        )

    @staticmethod
    def delete_by_name(db, user_id, item_name):
        """Deletes inventory items matching the name for a user"""
        InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE user_id = ? AND item_name = ?',
            (user_id, item_name)
        )

    @staticmethod
    def get_by_name(db, user_id, item_name):
        """Gets inventory items by name for a user"""
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE user_id = ? AND item_name LIKE ?',
            (user_id, f"%{item_name}%")
        )

    @staticmethod
    def adjust_quantity(db, item_id, amount):
        """Adjusts inventory quantity by amount (positive or negative)"""
        InventoryModel._execute_update(
            db,
            'UPDATE inventory SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (amount, item_id)
        )
