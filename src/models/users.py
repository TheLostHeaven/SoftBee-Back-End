def init(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            reset_token TEXT,
            reset_token_expiry DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    db.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')

class User:
    def __init__(self, **kwargs):
        self.nombre = kwargs.get('nombre')
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.phone = kwargs.get('phone')
        self.password = kwargs.get('password')


    @staticmethod
    def get_by_id(user_id):
        db = db.get_db()
        return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    def save(self):
        db = db.get_db()
        if hasattr(self, 'id'):
            db.execute('''
                UPDATE users 
                SET nombre=?, username=?, email=?, phone=?, password=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (self.nombre, self.username, self.email, self.phone, self.password, self.id))
        else:
            cursor = db.execute('''
                INSERT INTO users (nombre, username, email, phone, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.nombre, self.username, self.email, self.phone, self.password))
            self.id = cursor.lastrowid

        @staticmethod
        def delete(username):
            db = db.get_db()
            db.execute('DELETE FROM users WHERE id = ?', (username,))
            db.commit()