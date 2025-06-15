def init(db):
    db.execute('''
        CREATE TABLE IF NOT EXISTS apiary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user INTEGER NOT NULL,
            nombre_apiario TEXT NOT NULL,
            direccion TEXT NOT NULL,
            cantidad_colmenas INTEGER NOT NULL,
            latitud REAL NOT NULL,
            longitud REAL NOT NULL,
            aplica_tratamiento BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    db.execute('CREATE INDEX IF NOT EXISTS idx_apiary_user ON apiary(id_user)')

    class Apiary:
        def __init__(self, **kwargs):
            self.id = kwargs.get('id')
            self.id_user = kwargs.get('id_user')
            self.nombre_apiario = kwargs.get('nombre_apiario')
            self.direccion = kwargs.get('direccion')
            self.cantidad_colmenas = kwargs.get('cantidad_colmenas')
            self.latitud = kwargs.get('latitud')
            self.longitud = kwargs.get('longitud')
            self.aplica_tratamiento = kwargs.get('aplica_tratamiento', False)

        @staticmethod
        def get_by_id(apiary_id):
            db = db.get_db()
            return db.execute('SELECT * FROM apiary WHERE id = ?', (apiary_id,)).fetchone()

        def save(self):
            db = db.get_db()
            if hasattr(self, 'id'):
                db.execute('''
                    UPDATE apiary 
                    SET id_user=?, nombre_apiario=?, direccion=?, cantidad_colmenas=?, latitud=?, longitud=?, aplica_tratamiento=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (self.id_user, self.nombre_apiario, self.direccion, self.cantidad_colmenas, self.latitud, self.longitud, self.aplica_tratamiento, self.id))
            else:
                cursor = db.execute('''
                    INSERT INTO apiary (id_user, nombre_apiario, direccion, cantidad_colmenas, latitud, longitud, aplica_tratamiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (self.id_user, self.nombre_apiario, self.direccion, self.cantidad_colmenas, self.latitud, self.longitud, self.aplica_tratamiento))
                self.id = cursor.lastrowid
            db.commit()