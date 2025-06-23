import os
import sqlite3

class InventoryModel:
    @staticmethod
    def init_db(db):
        """Inicializa la tabla de inventario (compatible SQLite y PostgreSQL)"""
        cursor = db.cursor()
        try:            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id {id_type},
                    apiary_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit TEXT NOT NULL DEFAULT 'unit',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
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
        """Ejecuta consultas con placeholders universales"""
        cursor = db.execute(query, params)
        try:
            # Manejo compatible para obtener nombres de columnas
            columns = [col[0] for col in cursor.description]
        except Exception:
            # Para PostgreSQL que no devuelve description hasta después de fetch
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def _execute_single_query(db, query, params=()):
        """Ejecuta consulta y devuelve un solo resultado"""
        cursor = db.execute(query, params)
        row = cursor.fetchone()
        if not row:
            return None
        
        try:
            # Manejo compatible para obtener nombres de columnas
            columns = [col[0] for col in cursor.description]
        except Exception:
            # Para PostgreSQL
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
        return dict(zip(columns, row))

    @staticmethod
    def _execute_update(db, query, params=()):
        """Ejecuta actualizaciones con placeholders universales"""
        cursor = db.execute(query, params)
        if hasattr(db, 'commit'):
            db.commit()
        return cursor

    @staticmethod
    def get_all(db, apiary_id):
        """Obtiene todo el inventario de un apiario (compatible)"""
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE apiary_id = %s ORDER BY id',
            (apiary_id,)
        )

    @staticmethod
    def get_by_id(db, item_id):
        """Obtiene un ítem por ID (compatible)"""
        return InventoryModel._execute_single_query(
            db,
            'SELECT * FROM inventory WHERE id = %s',
            (item_id,)
        )

    @staticmethod
    def create(db, apiary_id, item_name, quantity=0, unit='unit'):
        """Crea un nuevo ítem en el inventario (compatible)"""
        is_postgres = 'postgresql' in os.environ.get('DATABASE_URL', '')
        
        if is_postgres:
            # PostgreSQL necesita RETURNING para obtener el ID
            query = '''
                INSERT INTO inventory (apiary_id, item_name, quantity, unit)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            '''
            cursor = db.execute(query, (apiary_id, item_name, quantity, unit))
            if hasattr(db, 'commit'):
                db.commit()
            return cursor.fetchone()[0]
        else:
            # SQLite usa lastrowid
            cursor = InventoryModel._execute_update(
                db,
                'INSERT INTO inventory (apiary_id, item_name, quantity, unit) VALUES (%s, %s, %s, %s)',
                (apiary_id, item_name, quantity, unit)
            )
            return cursor.lastrowid

    @staticmethod
    def update(db, item_id, item_name=None, quantity=None, unit=None):
        """Actualiza un ítem (compatible)"""
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
        """Elimina un ítem (compatible)"""
        InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE id = %s',
            (item_id,)
        )

    @staticmethod
    def delete_by_name(db, apiary_id, item_name):
        """Elimina ítem por nombre (compatible)"""
        InventoryModel._execute_update(
            db,
            'DELETE FROM inventory WHERE apiary_id = %s AND item_name = %s',
            (apiary_id, item_name)
        )

    @staticmethod
    def get_by_name(db, apiary_id, item_name):
        """Busca ítems por nombre (compatible)"""
        return InventoryModel._execute_query(
            db,
            'SELECT * FROM inventory WHERE apiary_id = %s AND item_name LIKE %s',
            (apiary_id, f"%{item_name}%")
        )

    @staticmethod
    def adjust_quantity(db, item_id, amount):
        """Ajusta la cantidad de un ítem (compatible)"""
        InventoryModel._execute_update(
            db,
            'UPDATE inventory SET quantity = quantity + %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s',
            (amount, item_id)
        )