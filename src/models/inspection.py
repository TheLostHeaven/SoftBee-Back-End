def init(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS inspection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            beehive_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            respuesta TEXT NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (beehive_id) REFERENCES beehive(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE,
            UNIQUE(beehive_id, question_id, fecha)
        )
    ''')

    db.execute('CREATE INDEX IF NOT EXISTS idx_inspection_beehive ON inspection(beehive_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_inspection_question ON inspection(question_id)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_inspection_fecha ON inspection(fecha)')


class Inspection:

    @staticmethod
    def create(beehive_id, question_id, respuesta):
        """Crea un nuevo registro de inspección"""
        db = db.get_db()
        return db.execute('''
                INSERT INTO inspection (beehive_id, question_id, respuesta)
                VALUES (?, ?, ?)
            ''', (beehive_id, question_id, respuesta))

    @staticmethod
    def get_by_beehive(beehive_id):
        db = db.get_db()
        return db.execute('''
            SELECT i.*, q.pregunta 
            FROM inspection i
            JOIN question q ON i.question_id = q.id
            WHERE i.beehive_id = ?
            ORDER BY i.fecha DESC
        ''', (beehive_id,)).fetchall()
    
    @staticmethod
    def get_latest_by_beehive(beehive_id, limit=5):
        db = db.get_db()
        return db.execute('''
            SELECT i.*, q.pregunta 
            FROM inspection i
            JOIN question q ON i.question_id = q.id
            WHERE i.beehive_id = ?
            ORDER BY i.fecha DESC
            LIMIT ?
        ''', (beehive_id, limit)).fetchall()
    
    @staticmethod
    def get_responses_for_question(beehive_id, question_id, limit=10):
    
        db = db.get_db()
        return db.execute('''
            SELECT respuesta, fecha 
            FROM inspection
            WHERE beehive_id = ? AND question_id = ?
            ORDER BY fecha DESC
            LIMIT ?
        ''', (beehive_id, question_id, limit)).fetchall()