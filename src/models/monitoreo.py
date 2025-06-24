import json
from datetime import datetime

class MonitoreoModel:
    @staticmethod
    def init_db(db):
        """Inicializa las tablas de monitoreo"""
        cursor = db.cursor()
        try:
            # Tabla de monitoreos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoreos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_colmena INTEGER NOT NULL,
                    id_apiario INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    datos_json TEXT,
                    sincronizado INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_colmena) REFERENCES colmenas(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_apiario) REFERENCES apiarios(id) ON DELETE CASCADE
                )
            ''')
            
            # Tabla de respuestas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS respuestas_monitoreo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitoreo_id INTEGER NOT NULL,
                    pregunta_id TEXT NOT NULL,
                    pregunta_texto TEXT NOT NULL,
                    respuesta TEXT,
                    tipo_respuesta TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (monitoreo_id) REFERENCES monitoreos(id) ON DELETE CASCADE
                )
            ''')
            
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def create(db, id_colmena, id_apiario, fecha, respuestas=None, datos_adicionales=None):
        """Crea un nuevo monitoreo"""
        cursor = db.cursor()
        try:
            # Crear el monitoreo principal
            datos_json = json.dumps(datos_adicionales) if datos_adicionales else None
            
            cursor.execute('''
                INSERT INTO monitoreos (id_colmena, id_apiario, fecha, datos_json)
                VALUES (?, ?, ?, ?)
            ''', (id_colmena, id_apiario, fecha, datos_json))
            
            monitoreo_id = cursor.lastrowid
            
            # Insertar respuestas si las hay
            if respuestas:
                for respuesta in respuestas:
                    cursor.execute('''
                        INSERT INTO respuestas_monitoreo 
                        (monitoreo_id, pregunta_id, pregunta_texto, respuesta, tipo_respuesta)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        monitoreo_id,
                        respuesta.get('pregunta_id'),
                        respuesta.get('pregunta_texto'),
                        str(respuesta.get('respuesta')),
                        respuesta.get('tipo_respuesta', 'texto')
                    ))
            
            db.commit()
            return monitoreo_id
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(db, monitoreo_id):
        """Obtiene un monitoreo por ID con sus respuestas"""
        cursor = db.cursor()
        try:
            # Obtener monitoreo principal
            cursor.execute('''
                SELECT m.*, a.nombre as apiario_nombre, c.numero_colmena
                FROM monitoreos m
                JOIN apiarios a ON m.id_apiario = a.id
                JOIN colmenas c ON m.id_colmena = c.id
                WHERE m.id = ?
            ''', (monitoreo_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            monitoreo = dict(row)
            
            # Obtener respuestas
            cursor.execute('''
                SELECT * FROM respuestas_monitoreo 
                WHERE monitoreo_id = ?
                ORDER BY id
            ''', (monitoreo_id,))
            
            respuestas = [dict(row) for row in cursor.fetchall()]
            monitoreo['respuestas'] = respuestas
            
            # Parsear datos JSON si existen
            if monitoreo.get('datos_json'):
                monitoreo['datos_adicionales'] = json.loads(monitoreo['datos_json'])
            
            return monitoreo
            
        finally:
            cursor.close()

    @staticmethod
    def get_all(db, limit=100, offset=0):
        """Obtiene todos los monitoreos con paginación"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT m.*, a.nombre as apiario_nombre, c.numero_colmena
                FROM monitoreos m
                JOIN apiarios a ON m.id_apiario = a.id
                JOIN colmenas c ON m.id_colmena = c.id
                ORDER BY m.fecha DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            cursor.close()

    @staticmethod
    def get_by_apiario(db, apiario_id):
        """Obtiene monitoreos por apiario"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT m.*, c.numero_colmena
                FROM monitoreos m
                JOIN colmenas c ON m.id_colmena = c.id
                WHERE m.id_apiario = ?
                ORDER BY m.fecha DESC
            ''', (apiario_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            cursor.close()

    @staticmethod
    def get_by_colmena(db, colmena_id):
        """Obtiene monitoreos por colmena"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT m.*, a.nombre as apiario_nombre
                FROM monitoreos m
                JOIN apiarios a ON m.id_apiario = a.id
                WHERE m.id_colmena = ?
                ORDER BY m.fecha DESC
            ''', (colmena_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            cursor.close()

    @staticmethod
    def update(db, monitoreo_id, **kwargs):
        """Actualiza un monitoreo"""
        if not kwargs:
            raise ValueError("No fields to update")
        
        cursor = db.cursor()
        try:
            fields = []
            params = []
            
            for field, value in kwargs.items():
                if field in ['id_colmena', 'id_apiario', 'fecha', 'datos_json', 'sincronizado']:
                    fields.append(f"{field} = ?")
                    params.append(value)
            
            if not fields:
                raise ValueError("No valid fields to update")
            
            params.append(monitoreo_id)
            query = f"UPDATE monitoreos SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            
            cursor.execute(query, params)
            db.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def delete(db, monitoreo_id):
        """Elimina un monitoreo y sus respuestas"""
        cursor = db.cursor()
        try:
            # Las respuestas se eliminan automáticamente por CASCADE
            cursor.execute('DELETE FROM monitoreos WHERE id = ?', (monitoreo_id,))
            db.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def mark_as_synced(db, monitoreo_id):
        """Marca un monitoreo como sincronizado"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                UPDATE monitoreos 
                SET sincronizado = 1, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (monitoreo_id,))
            
            db.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def get_pending_sync(db):
        """Obtiene monitoreos pendientes de sincronización"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT m.*, a.nombre as apiario_nombre, c.numero_colmena
                FROM monitoreos m
                JOIN apiarios a ON m.id_apiario = a.id
                JOIN colmenas c ON m.id_colmena = c.id
                WHERE m.sincronizado = 0
                ORDER BY m.fecha ASC
            ''', )
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            cursor.close()
