from src.models.monitoreo import MonitoreoModel

class ReportsController:
    def __init__(self, db):
        self.db = db
        self.monitoreo_model = MonitoreoModel

    def get_monitoring_reports(self, user_id):
        """Obtiene todos los monitoreos para un usuario con un formato para reportes."""
        try:
            reports = self.monitoreo_model.get_all_with_details(self.db, user_id)
            return reports

        except Exception as e:
            print(f"Error en ReportsController: {e}")
            raise e