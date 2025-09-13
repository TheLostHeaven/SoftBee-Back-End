from datetime import datetime
from src.models.monitoreo import MonitoreoModel
from flask import current_app

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

    def get_system_stats(self, user_id):
        """Obtiene estadísticas del sistema para un usuario específico"""
        current_app.logger.info(f"Getting system stats for user_id: {user_id}")
        cursor = self.db.cursor()

        try:
            # Total de apiarios para el usuario
            current_app.logger.debug("Executing total_apiarios query")
            cursor.execute("SELECT COUNT(*) FROM apiaries WHERE user_id = %s", (user_id,))
            total_apiarios = cursor.fetchone()[0]
            current_app.logger.debug(f"total_apiarios: {total_apiarios}")

            # Total de colmenas para el usuario
            current_app.logger.debug("Executing total_colmenas query")
            cursor.execute("SELECT COUNT(*) FROM hives WHERE apiary_id IN (SELECT id FROM apiaries WHERE user_id = %s)", (user_id,))
            total_colmenas = cursor.fetchone()[0]
            current_app.logger.debug(f"total_colmenas: {total_colmenas}")

            # Total de monitoreos para el usuario
            current_app.logger.debug("Executing total_monitoreos query")
            cursor.execute("SELECT COUNT(*) FROM monitoreos WHERE apiary_id IN (SELECT id FROM apiaries WHERE user_id = %s)", (user_id,))
            total_monitoreos = cursor.fetchone()[0]
            current_app.logger.debug(f"total_monitoreos: {total_monitoreos}")

            # Monitoreos pendientes para el usuario
            current_app.logger.debug("Executing monitoreos_pendientes query")
            cursor.execute("SELECT COUNT(*) FROM monitoreos WHERE sincronizado = FALSE AND apiary_id IN (SELECT id FROM apiaries WHERE user_id = %s)", (user_id,))
            monitoreos_pendientes = cursor.fetchone()[0]
            current_app.logger.debug(f"monitoreos_pendientes: {monitoreos_pendientes}")

            # Monitoreos del último mes para el usuario
            current_app.logger.debug("Executing monitoreos_mes query")
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            cursor.execute("""
                SELECT COUNT(*) FROM monitoreos 
                WHERE fecha >= %s AND apiary_id IN (SELECT id FROM apiaries WHERE user_id = %s)
            """, (thirty_days_ago, user_id,))
            monitoreos_mes = cursor.fetchone()[0]
            current_app.logger.debug(f"monitoreos_mes: {monitoreos_mes}")

            # Monitoreos por apiario para el usuario
            current_app.logger.debug("Executing monitoreos_por_apiario query")
            cursor.execute("""
                SELECT a.name, COUNT(m.id) as total
                FROM apiaries a
                LEFT JOIN monitoreos m ON a.id = m.apiary_id
                WHERE a.user_id = %s
                GROUP BY a.id, a.name
                ORDER BY total DESC
            """, (user_id,))
            monitoreos_por_apiario = [
                {'apiario': row[0], 'total': row[1]} 
                for row in cursor.fetchall()
            ]
            current_app.logger.debug(f"monitoreos_por_apiario: {monitoreos_por_apiario}")

            stats = {
                'total_apiarios': total_apiarios,
                'total_colmenas': total_colmenas,
                'total_monitoreos': total_monitoreos,
                'monitoreos_pendientes': monitoreos_pendientes,
                'monitoreos_ultimo_mes': monitoreos_mes,
                'monitoreos_por_apiario': monitoreos_por_apiario,
                'timestamp': datetime.utcnow().isoformat()
            }
            current_app.logger.info(f"Successfully generated stats: {stats}")
            return stats
        except Exception as e:
            current_app.logger.error(f"Error in get_system_stats for user {user_id}: {e}", exc_info=True)
            raise
