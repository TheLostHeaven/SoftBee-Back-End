from src.models.monitoreo import MonitoreoModel

class ReportsController:
    def __init__(self, db):
        self.db = db
        self.monitoreo_model = MonitoreoModel

    def get_monitoring_reports(self, user_id):
        """Obtiene todos los monitoreos para un usuario con un formato para reportes."""
        try:
            # Esta función podría necesitar ser implementada en el modelo
            # para filtrar por usuario de manera más directa.
            # Por ahora, asumimos que get_all trae todos y filtramos aquí si es necesario,
            # o mejor, lo adaptamos para que el modelo lo haga.
            
            # Lo ideal es tener un método en el modelo que acepte user_id
            # Por ejemplo: self.monitoreo_model.get_all_by_user(self.db, user_id)
            
            # Asumiendo que get_all_monitoreos no filtra por usuario, 
            # necesitaremos una lógica más compleja aquí o en el modelo.
            # Por simplicidad, vamos a crear un método en el modelo.
            
            reports = self.monitoreo_model.get_all_with_details(self.db, user_id)
            
            return reports

        except Exception as e:
            # Manejo de errores más específico podría ser necesario
            print(f"Error en ReportsController: {e}")
            raise e
