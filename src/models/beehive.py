def init(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS beehive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apiary_id INTEGER NOT NULL,
            queen_year INTEGER,
            hive_type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (apiary_id) REFERENCES apiary(id) ON DELETE CASCADE
        )
    ''')

    db.execute('CREATE INDEX IF NOT EXISTS idx_beehive_apiary ON beehive(apiary_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_beehive_queen_year ON beehive(queen_year)')


class Beehive:
    def __init__(self, **kwargs):
        self.nombre = kwargs.get('nombre')
        self.apiary_id = kwargs.get('apiary_id')
        self.queen_year = kwargs.get('queen_year')
        self.hive_type = kwargs.get('hive_type')

    @staticmethod

    def get_by_apiary(apiary_id):
        db = db.get_db()
        return db.execute(
            'SELECT * FROM beehive WHERE apiary_id = ? ORDER BY nombre',
            (apiary_id,)
        ).fetchall()
    
    def get_by_id(beehive_id):
        db = db.get_db()
        return db.execute('SELECT * FROM beehive WHERE id = ?', (beehive_id,)).fetchone()
    


    def save(self):
        db = db.get_db()
        if hasattr(self, 'id'):
            db.execute('''
                UPDATE beehive 
                SET nombre=?, apiary_id=?, queen_year=?, hive_type=?
                WHERE id=?
            ''', (self.nombre, self.apiary_id, self.queen_year, self.hive_type, self.id))
        else:
            cursor = db.execute('''
                INSERT INTO beehive (nombre, apiary_id, queen_year, hive_type)
                VALUES (?, ?, ?, ?)
            ''', (self.nombre, self.apiary_id, self.queen_year, self.hive_type))
            self.id = cursor.lastrowid

    @staticmethod
    def delete(beehive_id):
        db = db.get_db()
        db.execute('DELETE FROM beehive WHERE id = ?', (beehive_id,))
        db.commit()