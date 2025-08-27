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
                    description TEXT,
                    minimum_stock INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE,
                    UNIQUE(apiary_id, name)
                )
            ''')
            
            # Crear índices para mejorar el rendimiento
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_apiary_id ON inventory(apiary_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_name ON inventory(apiary_id, name)')
            
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
    def create(db, apiary_id, name, quantity=0, unit='unit', description=None, minimum_stock=0):
        # Verificar que el apiario existe
        cursor = db.cursor()
        cursor.execute('SELECT id FROM apiaries WHERE id = %s', (apiary_id,))
        if not cursor.fetchone():
            cursor.close()
            raise ValueError(f"Apiary with id {apiary_id} does not exist")
        cursor.close()
        
        query = '''
            INSERT INTO inventory (apiary_id, name, quantity, unit, description, minimum_stock)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        '''
        cursor = db.cursor()
        try:
            cursor.execute(query, (apiary_id, name, quantity, unit, description, minimum_stock))
            db.commit()
            item_id = cursor.fetchone()[0]
            return item_id
        except psycopg2.IntegrityError as e:
            db.rollback()
            if 'unique' in str(e).lower():
                raise ValueError(f"Item '{name}' already exists in this apiary")
            raise e
        finally:
            cursor.close()

    @staticmethod
    def update(db, item_id, name=None, quantity=None, unit=None, description=None, minimum_stock=None):
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
        if description is not None:
            fields.append("description = %s")
            params.append(description)
        if minimum_stock is not None:
            fields.append("minimum_stock = %s")
            params.append(minimum_stock)

        if not fields:
            raise ValueError("No fields to update")

        params.append(item_id)
        query = f"UPDATE inventory SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        
        try:
            InventoryModel._execute_update(db, query, params)
        except psycopg2.IntegrityError as e:
            if 'unique' in str(e).lower():
                raise ValueError(f"Item name already exists in this apiary")
            raise e

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
            '''SELECT i.*, a.name as apiary_name FROM inventory i
            JOIN apiaries a ON i.apiary_id = a.id
            WHERE a.user_id = %s
            ORDER BY a.name, i.name''',
            (user_id,)
        )

    @staticmethod
    def get_low_stock_items(db, apiary_id):
        """Obtiene items con stock bajo (cantidad <= stock mínimo)"""
        return InventoryModel._execute_query(
            db,
            '''SELECT * FROM inventory 
            WHERE apiary_id = %s AND quantity <= minimum_stock
            ORDER BY name''',
            (apiary_id,)
        )

    @staticmethod
    def get_apiary_summary(db, apiary_id):
        """Obtiene un resumen del inventario del apiario"""
        return InventoryModel._execute_single_query(
            db,
            '''SELECT 
                COUNT(*) as total_items,
                SUM(quantity) as total_quantity,
                COUNT(CASE WHEN quantity <= minimum_stock THEN 1 END) as low_stock_items
            FROM inventory 
            WHERE apiary_id = %s''',
            (apiary_id,)
        )

    @staticmethod
    def validate_apiary_access(db, item_id, user_id):
        """Valida que el usuario tenga acceso al item a través de su apiario"""
        result = InventoryModel._execute_single_query(
            db,
            '''SELECT i.id FROM inventory i
            JOIN apiaries a ON i.apiary_id = a.id
            WHERE i.id = %s AND a.user_id = %s''',
            (item_id, user_id)
        )
        return result is not None

    @staticmethod
    def get_item_with_apiary(db, item_id):
        """Obtiene un item con información del apiario"""
        return InventoryModel._execute_single_query(
            db,
            '''SELECT i.*, a.name as apiary_name, a.user_id
            FROM inventory i
            JOIN apiaries a ON i.apiary_id = a.id
            WHERE i.id = %s''',
            (item_id,)
        )