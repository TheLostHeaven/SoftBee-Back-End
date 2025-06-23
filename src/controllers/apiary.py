from ..models.apiary import ApiaryModel

class ApiaryController:
    def __init__(self, db):
        self.db = db
        self.model = ApiaryModel
    
    def create_apiary(self, user_id, name, location=None):
        cursor = None
        try:
            cursor = self.db.cursor()
            # Sintaxis PostgreSQL con RETURNING
            cursor.execute(
                "INSERT INTO apiaries (user_id, name, location) "
                "VALUES (%s, %s, %s) RETURNING id",
                (user_id, name, location)
            )
            result = cursor.fetchone()
            return result[0]  # Retorna el ID del nuevo apiario
        finally:
            if cursor:
                cursor.close()
    
    def get_all_apiaries_for_user(self, user_id):
        """Gets all apiaries for a user"""
        return self.model.get_by_user(self.db, user_id)
    
    def update_apiary(self, apiary_id, **kwargs):
        """Updates apiary information"""
        self.model.update(self.db, apiary_id, **kwargs)
    
    def delete_apiary(self, apiary_id):
        """Deletes an apiary"""
        self.model.delete(self.db, apiary_id)
