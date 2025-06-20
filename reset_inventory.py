import sqlite3

# Abre conexión (o crea el archivo si no existe)
db = sqlite3.connect("database.db")

try:
    db.execute('DROP TABLE IF EXISTS inventory')
    print("Tabla inventory eliminada")

    db.execute('''
        CREATE TABLE inventory (
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
    print("Tabla inventory creada")

    db.execute('CREATE INDEX idx_inventory_apiary_id ON inventory(apiary_id)')
    db.execute('CREATE INDEX idx_inventory_item_name ON inventory(item_name)')
    print("Índices creados")

    db.commit()
except sqlite3.Error as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
