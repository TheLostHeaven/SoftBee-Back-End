def init(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS apiary_access (
            user_id INTEGER NOT NULL,
            apiary_id INTEGER NOT NULL,
            permission_level INTEGER DEFAULT 1, 
            PRIMARY KEY (user_id, apiary_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (apiary_id) REFERENCES apiary(id) ON DELETE CASCADE
        )
    ''')
    
    db.execute('CREATE INDEX IF NOT EXISTS idx_access_user ON apiary_access(user_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_access_apiary ON apiary_access(apiary_id)')

class ApiaryAccess:
    READ = 1
    WRITE = 2
    ADMIN = 3
    
    @staticmethod
    def grant_access(user_id, apiary_id, permission_level=READ):
        """Concede acceso a un apiario"""
        db = db.get_db()
        db.execute('''
            INSERT INTO apiary_access (user_id, apiary_id, permission_level)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, apiary_id) DO UPDATE SET
                permission_level = excluded.permission_level
        ''', (user_id, apiary_id, permission_level))
        db.commit()
    
    @staticmethod
    def revoke_access(user_id, apiary_id):
        """Revoca el acceso a un apiario"""
        db = db.get_db()
        db.execute('''
            DELETE FROM apiary_access 
            WHERE user_id = ? AND apiary_id = ?
        ''', (user_id, apiary_id))
        db.commit()
    
    @staticmethod
    def get_user_permissions(user_id):
        """Obtiene todos los apiarios a los que tiene acceso un usuario"""
        db = db.get_db()
        return db.execute('''
            SELECT a.*, aa.permission_level
            FROM apiary a
            JOIN apiary_access aa ON a.id = aa.apiary_id
            WHERE aa.user_id = ?
        ''', (user_id,)).fetchall()
    
    @staticmethod
    def check_permission(user_id, apiary_id, required_level=READ):
        """Verifica si un usuario tiene un permiso específico"""
        db = db.get_db()
        access = db.execute('''
            SELECT permission_level 
            FROM apiary_access
            WHERE user_id = ? AND apiary_id = ?
        ''', (user_id, apiary_id)).fetchone()
        
        return access and access['permission_level'] >= required_level
    
    