from datetime import datetime
from src.models.monitoreo import MonitoreoModel

class MonitoreoController:
    def __init__(self, db):
        self.db = db
        self.model = MonitoreoModel

    def create_monitoreo(self, id_colmena, id_apiario, fecha=None, respuestas=None, datos_adicionales=None):
        """Crea un nuevo monitoreo"""
        if fecha is None:
            fecha = datetime.utcnow().isoformat()
        
        # Validar que la colmena existe
        cursor = self.db.cursor()
        cursor.execute("SELECT id FROM colmenas WHERE id = %s", (id_colmena,))
        if not cursor.fetchone():
            raise ValueError("Colmena no encontrada")
        
        # Validar que el apiario existe
        cursor.execute("SELECT id FROM apiarios WHERE id = %s", (id_apiario,))
        if not cursor.fetchone():
            raise ValueError("Apiario no encontrado")
        
        return self.model.create(
            self.db, 
            id_colmena, 
            id_apiario, 
            fecha, 
            respuestas or [], 
            datos_adicionales
        )

    def get_monitoreo(self, monitoreo_id):
        """Obtiene un monitoreo por ID"""
        return self.model.get_by_id(self.db, monitoreo_id)

    def get_all_monitoreos(self):
        """Obtiene todos los monitoreos"""
        return self.model.get_all(self.db)

    def get_monitoreos_by_apiario(self, apiario_id):
        """Obtiene monitoreos por apiario"""
        return self.model.get_by_apiario(self.db, apiario_id)

    def get_monitoreos_by_colmena(self, colmena_id):
        """Obtiene monitoreos por colmena"""
        return self.model.get_by_colmena(self.db, colmena_id)

    def update_monitoreo(self, monitoreo_id, **kwargs):
        """Actualiza un monitoreo"""
        return self.model.update(self.db, monitoreo_id, **kwargs)

    def delete_monitoreo(self, monitoreo_id):
        """Elimina un monitoreo"""
        return self.model.delete(self.db, monitoreo_id)

    def get_system_stats(self):
        """Obtiene estadísticas del sistema"""
        cursor = self.db.cursor()
        
        # Total de apiarios
        cursor.execute("SELECT COUNT(*) FROM apiarios")
        total_apiarios = cursor.fetchone()[0]
        
        # Total de colmenas
        cursor.execute("SELECT COUNT(*) FROM colmenas")
        total_colmenas = cursor.fetchone()[0]
        
        # Total de monitoreos
        cursor.execute("SELECT COUNT(*) FROM monitoreos")
        total_monitoreos = cursor.fetchone()[0]
        
        # Monitoreos del último mes (PostgreSQL)
        cursor.execute("""
            SELECT COUNT(*) FROM monitoreos 
            WHERE fecha >= CURRENT_DATE - INTERVAL '30 days'
        """)
        monitoreos_mes = cursor.fetchone()[0]
        
        # Monitoreos por apiario
        cursor.execute("""
            SELECT a.nombre, COUNT(m.id) as total
            FROM apiarios a
            LEFT JOIN monitoreos m ON a.id = m.id_apiario
            GROUP BY a.id, a.nombre
            ORDER BY total DESC
        """)
        monitoreos_por_apiario = [
            {'apiario': row[0], 'total': row[1]} 
            for row in cursor.fetchall()
        ]
        
        return {
            'total_apiarios': total_apiarios,
            'total_colmenas': total_colmenas,
            'total_monitoreos': total_monitoreos,
            'monitoreos_ultimo_mes': monitoreos_mes,
            'monitoreos_por_apiario': monitoreos_por_apiario,
            'timestamp': datetime.utcnow().isoformat()
        }
