import json
from datetime import datetime

class MonitoreoModel:
    @staticmethod
    def init_db(db):
        """Inicializa las tablas de monitoreo en PostgreSQL"""
        cursor = db.cursor()
        try:
            # Tabla de monitoreos con tipos específicos de PostgreSQL
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoreos (
                    id SERIAL PRIMARY KEY,
                    beehive_id INTEGER NOT NULL,
                    apiary_id INTEGER NOT NULL,
                    fecha TIMESTAMP NOT NULL,
                    datos_json JSONB,
                    sincronizado BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (beehive_id) REFERENCES beehives(id) ON DELETE CASCADE,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
                )
            ''')
            
            # Tabla de respuestas con tipos optimizados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS respuestas_monitoreo (
                    id SERIAL PRIMARY KEY,
                    monitoreo_id INTEGER NOT NULL,
                    pregunta_id TEXT NOT NULL,
                    pregunta_texto TEXT NOT NULL,
                    respuesta TEXT,
                    tipo_respuesta TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (monitoreo_id) REFERENCES monitoreos(id) ON DELETE CASCADE
                )
            ''')
            
            # Crear índices para mejor rendimiento
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_monitoreos_fecha 
                ON monitoreos (fecha)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_monitoreos_apiario 
                ON monitoreos (apiary_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_monitoreos_colmena 
                ON monitoreos (beehive_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_respuestas_monitoreo_id 
                ON respuestas_monitoreo (monitoreo_id)
            ''')
            
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def _rows_to_dicts(cursor):
        """Convierte los resultados del cursor en diccionarios"""
        if cursor.description is None:
            return []
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def create(db, beehive_id, apiary_id, fecha, respuestas=None, datos_adicionales=None):
        """Crea un nuevo monitoreo en PostgreSQL"""
        cursor = db.cursor()
        try:
            # Usar tipo JSONB nativo de PostgreSQL
            datos_json = json.dumps(datos_adicionales) if datos_adicionales else None
            
            # Insertar monitoreo principal y obtener ID creado
            cursor.execute('''
                INSERT INTO monitoreos (beehive_id, apiary_id, fecha, datos_json)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (beehive_id, apiary_id, fecha, datos_json))
            
            monitoreo_id = cursor.fetchone()[0]
            
            # Insertar respuestas usando ejecución múltiple si hay muchas
            if respuestas:
                respuestas_data = [
                    (
                        monitoreo_id,
                        respuesta.get('pregunta_id'),
                        respuesta.get('pregunta_texto'),
                        str(respuesta.get('respuesta')),
                        respuesta.get('tipo_respuesta', 'texto')
                    )
                    for respuesta in respuestas
                ]
                
                cursor.executemany('''
                    INSERT INTO respuestas_monitoreo 
                    (monitoreo_id, pregunta_id, pregunta_texto, respuesta, tipo_respuesta)
                    VALUES (%s, %s, %s, %s, %s)
                ''', respuestas_data)
            
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
                SELECT m.*, a.name as apiario_nombre, h.hive_number
                FROM monitoreos m
                JOIN apiaries a ON m.apiary_id = a.id
                JOIN beehives h ON m.beehive_id = h.id
                WHERE m.id = %s
            ''', (monitoreo_id,))
            
            monitoreo = cursor.fetchone()
            if not monitoreo:
                return None
            
            # Convertir a diccionario
            columns = [desc[0] for desc in cursor.description]
            monitoreo_dict = dict(zip(columns, monitoreo))
            
            # Obtener respuestas
            cursor.execute('''
                SELECT * FROM respuestas_monitoreo 
                WHERE monitoreo_id = %s
                ORDER BY id
            ''', (monitoreo_id,))
            
            respuestas = MonitoreoModel._rows_to_dicts(cursor)
            monitoreo_dict['respuestas'] = respuestas
            
            # Los datos JSONB se parsean automáticamente
            if monitoreo_dict.get('datos_json'):
                monitoreo_dict['datos_adicionales'] = monitoreo_dict['datos_json']
            
            return monitoreo_dict
            
        finally:
            cursor.close()

    @staticmethod
    def get_all(db, limit=100, offset=0):
        """Obtiene todos los monitoreos con paginación"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT m.*, a.name as apiario_nombre, h.hive_number
                FROM monitoreos m
                JOIN apiaries a ON m.apiary_id = a.id
                JOIN beehives h ON m.beehive_id = h.id
                ORDER BY m.fecha DESC
                LIMIT %s OFFSET %s
            ''', (limit, offset))
            
            return MonitoreoModel._rows_to_dicts(cursor)
        finally:
            cursor.close()

    @staticmethod
    def get_by_apiario(db, apiary_id):
        """Obtiene monitoreos por apiario"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT m.*, h.hive_number
                FROM monitoreos m
                JOIN beehives h ON m.beehive_id = h.id
                WHERE m.apiary_id = %s
                ORDER BY m.fecha DESC
            ''', (apiary_id,))
            
            return MonitoreoModel._rows_to_dicts(cursor)
        finally:
            cursor.close()

    @staticmethod
    def get_by_colmena(db, beehive_id):
        """Obtiene monitoreos por colmena"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT m.*, a.name as apiario_nombre
                FROM monitoreos m
                JOIN apiaries a ON m.apiary_id = a.id
                WHERE m.beehive_id = %s
                ORDER BY m.fecha DESC
            ''', (beehive_id,))
            
            return MonitoreoModel._rows_to_dicts(cursor)
        finally:
            cursor.close()

    @staticmethod
    def get_all_with_details(db, user_id, limit=100, offset=0):
        """Obtiene todos los monitoreos de un usuario con detalles para reportes."""
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT 
                    m.id as monitoreo_id,
                    m.fecha,
                    a.id as apiario_id,
                    a.name as apiario_nombre,
                    h.id as colmena_id,
                    h.hive_number
                FROM monitoreos m
                JOIN apiaries a ON m.apiary_id = a.id
                JOIN beehives h ON m.beehive_id = h.id
                WHERE a.user_id = %s
                ORDER BY m.fecha DESC
                LIMIT %s OFFSET %s
            ''', (user_id, limit, offset))
            
            monitoreos = MonitoreoModel._rows_to_dicts(cursor)
            
            # Para cada monitoreo, obtener sus respuestas
            for monitoreo in monitoreos:
                cursor.execute('''
                    SELECT pregunta_texto, respuesta, tipo_respuesta
                    FROM respuestas_monitoreo
                    WHERE monitoreo_id = %s
                    ORDER BY id
                ''', (monitoreo['monitoreo_id'],))
                monitoreo['respuestas'] = MonitoreoModel._rows_to_dicts(cursor)
            
            return monitoreos
        finally:
            cursor.close()

    @staticmethod
    def update(db, monitoreo_id, **kwargs):
        """Actualiza un monitoreo en PostgreSQL"""
        if not kwargs:
            raise ValueError("No fields to update")
        
        cursor = db.cursor()
        try:
            set_clause = []
            params = []
            
            for field, value in kwargs.items():
                if field in ['id_colmena', 'id_apiario', 'fecha', 'datos_json', 'sincronizado']:
                    set_clause.append(f"{field} = %s")
                    params.append(value)
            
            if not set_clause:
                raise ValueError("No valid fields to update")
            
            params.append(monitoreo_id)
            query = f'''
                UPDATE monitoreos 
                SET {', '.join(set_clause)}, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            '''
            
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
            cursor.execute('DELETE FROM monitoreos WHERE id = %s', (monitoreo_id,))
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
                SET sincronizado = TRUE, updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
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
                SELECT m.*, a.name as apiario_nombre, h.hive_number
                FROM monitoreos m
                JOIN apiaries a ON m.apiary_id = a.id
                JOIN beehives h ON m.beehive_id = h.id
                WHERE m.sincronizado = FALSE
                ORDER BY m.fecha ASC
            ''')
            
            return MonitoreoModel._rows_to_dicts(cursor)
        finally:
            cursor.close()