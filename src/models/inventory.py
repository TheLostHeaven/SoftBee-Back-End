class InventoryModel:
    @staticmethod
    def init_db(db):
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unity TEXT NOT NULL DEFAULT 'unit',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_inventory_item_name ON inventory(item_name)')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        
    @staticmethod
    def _execute_query(db, query, params=()):
        """Executes a query and returns results"""
        return db.execute(query, params).fetchall()
    @staticmethod
    def _execute_update(db, query, params=()):
        """Executes an update and commits"""
        cursor = db.execute(query, params)
        db.commit()
        return cursor
    @staticmethod
    def get_all_raw(db):
        """Gets all inventory items (raw data)"""
        return InventoryModel._execute_query(db, 'SELECT * FROM inventory ORDER BY id')
    @staticmethod
    def get_by_id_raw(db, item_id):
        """Gets an inventory item by ID (raw data)"""
        return InventoryModel._execute_query(
            db, 
            'SELECT * FROM inventory WHERE id = ?', 
            (item_id,)
        )[0] if InventoryModel._execute_query(db, 'SELECT 1 FROM inventory WHERE id = ?', (item_id,)) else None
    @staticmethod
    def create_raw(db, item_name, quantity=0, unity='unit'):
        """Creates a new inventory item (raw operation)"""
        cursor = InventoryModel._execute_update(
            db,
            'INSERT INTO inventory (item_name, quantity, unity) '
            'VALUES (?, ?, ?)',
            (item_name, quantity, unity)
        )
        return cursor.lastrowid
    @staticmethod
    def update_raw(db, item_id, item_name=None, quantity=None, unity=None):
        """Updates an existing inventory item (raw operation)"""
        fields = []
        params = []
        if item_name is not None:
            fields.append('item_name = ?')
            params.append(item_name)
        if quantity is not None:
            fields.append('quantity = ?')
            params.append(quantity)
        if unity is not None:
            fields.append('unity = ?')
            params.append(unity)
        
        if not fields:
            raise ValueError("At least one field must be updated")
        
        params.append(item_id)
        query = f'UPDATE inventory SET {", ".join(fields)} WHERE id = ?'
        InventoryModel._execute_update(db, query, params)
    @staticmethod
    def delete_raw(db, item_id):
        """Deletes an inventory item (raw operation)"""
        if not InventoryModel._execute_query(db, 'SELECT 1 FROM inventory WHERE id = ?', (item_id,)):
            raise ValueError("Item not found")
        
        db.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
    @staticmethod
    def get_item_by_name(db, item_name):
        """Gets an inventory item by name (raw operation)"""
        return InventoryModel._execute_query(
            db, 
            'SELECT * FROM inventory WHERE item_name = ?', 
            (item_name,)
        )