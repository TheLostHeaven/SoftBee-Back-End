import sqlite3
from datetime import datetime, timedelta

class UserModel:
    @staticmethod
    def init_db(db):
        """Creates the users table if it doesn't exist"""
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    phone INTEGER NOT NULL,
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
        except sqlite3.Error as e:
            db.rollback()
            raise e

    @staticmethod
    def _execute_query(db, query, params=()):
        cursor = db.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def _execute_update(db, query, params=()):
        cursor = db.execute(query, params)
        db.commit()
        return cursor

    @staticmethod
    def get_all(db):
        """Gets all users"""
        return UserModel._execute_query(db, 'SELECT * FROM users ORDER BY id')

    @staticmethod
    def get_by_id(db, user_id):
        """Gets a user by ID"""
        result = UserModel._execute_query(db, 'SELECT * FROM users WHERE id = ?', (user_id,))
        return result[0] if result else None

    @staticmethod
    def get_by_username(db, username):
        """Gets a user by username"""
        result = UserModel._execute_query(db, 'SELECT * FROM users WHERE username = ?', (username,))
        return result[0] if result else None

    @staticmethod
    def get_by_email(db, email):
        """Gets a user by email"""
        result = UserModel._execute_query(db, 'SELECT * FROM users WHERE email = ?', (email,))
        return result[0] if result else None

    @staticmethod
    def create(db, nombre, username, email, phone, password):
        """Creates a new user"""
        cursor = UserModel._execute_update(
            db,
            'INSERT INTO users (nombre, username, email, phone, password) VALUES (?, ?, ?, ?, ?)',
            (nombre, username, email, phone, password)
        )
        return cursor.lastrowid

    @staticmethod
    def update(db, user_id, **kwargs):
        """Updates user fields"""
        fields = []
        params = []

        for key in ['nombre', 'username', 'email', 'phone', 'password']:
            if key in kwargs and kwargs[key] is not None:
                fields.append(f"{key} = ?")
                params.append(kwargs[key])

        if not fields:
            raise ValueError("No fields provided to update")

        params.append(user_id)
        query = f'''
            UPDATE users
            SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        UserModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, user_id):
        """Deletes a user"""
        UserModel._execute_update(db, 'DELETE FROM users WHERE id = ?', (user_id,))

    @staticmethod
    def set_reset_token(db, email, token, expiry_hours=1):
        """Sets reset token and expiry"""
        expiry = (datetime.now() + timedelta(hours=expiry_hours)).strftime("%Y-%m-%d %H:%M:%S")
        UserModel._execute_update(
            db,
            'UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE email = ?',
            (token, expiry, email)
        )

    @staticmethod
    def verify_reset_token(db, token):
        """Validates reset token"""
        result = UserModel._execute_query(
            db,
            'SELECT * FROM users WHERE reset_token = ? AND reset_token_expiry > datetime("now")',
            (token,)
        )
        return result[0] if result else None

    @staticmethod
    def update_password(db, user_id, new_password):
        """Updates password and clears reset token"""
        UserModel._execute_update(
            db,
            '''
            UPDATE users
            SET password = ?, reset_token = NULL, reset_token_expiry = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''',
            (new_password, user_id)
        )
