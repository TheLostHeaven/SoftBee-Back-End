class UserModel:
    @staticmethod
    def init_db(db):
        try:
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
        """Gets all users (raw data)"""
        return UserModel._execute_query(db, 'SELECT * FROM users ORDER BY id')
    
    @staticmethod
    def get_by_id_raw(db, user_id):
        """Gets a user by ID (raw data)"""
        return UserModel._execute_query(
            db, 
            'SELECT * FROM users WHERE id = ?', 
            (user_id,)
        )[0] if UserModel._execute_query(db, 'SELECT 1 FROM users WHERE id = ?', (user_id,)) else None
    
    @staticmethod
    def create_raw(db, nombre, username, email, phone, password):
        """Creates a new user (raw operation)"""
        cursor = UserModel._execute_update(
            db,
            'INSERT INTO users (nombre, username, email, phone, password) '
            'VALUES (?, ?, ?, ?, ?)',
            (nombre, username, email, phone, password)
        )
        return cursor.lastrowid
    
    @staticmethod
    def update_raw(db, user_id, nombre, username, email, phone, password):
        """Updates an existing user (raw operation)"""
        UserModel._execute_update(
            db,
            '''
            UPDATE users 
            SET nombre=?, username=?, email=?, phone=?, password=?, updated_at=CURRENT_TIMESTAMP 
            WHERE id=?
            ''',
            (nombre, username, email, phone, password, user_id)
        )

    @staticmethod
    def delete_raw(db, user_id):
        """Deletes a user by ID (raw operation)"""
        UserModel._execute_update(
            db,
            'DELETE FROM users WHERE id = ?',
            (user_id,)
        )
    @staticmethod
    def get_by_username(db, username):
        """Gets a user by username (raw data)"""
        return UserModel._execute_query(
            db, 
            'SELECT * FROM users WHERE username = ?', 
            (username,)
        )[0] if UserModel._execute_query(db, 'SELECT 1 FROM users WHERE username = ?', (username,)) else None