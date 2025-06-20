import sqlite3

conn = sqlite3.connect('database.db')
try:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS apiaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            location TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    print("Tabla apiaries creada.")
except sqlite3.Error as e:
    print("Error:", e)
finally:
    conn.close()
