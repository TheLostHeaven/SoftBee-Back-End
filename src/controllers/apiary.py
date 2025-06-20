from ..models.apiary import ApiaryModel

class ApiaryController:
    def __init__(self, db):
        self.db = db
        self.model = ApiaryModel
    
    def create_apiary(self, user_id, name, location=None):
        """Creates a new apiary for a user"""
        return self.model.create(self.db, user_id, name, location)
    
    def get_apiary(self, apiary_id):
        """Gets apiary by ID"""
        return self.model.get_by_id(self.db, apiary_id)
    
    def get_all_apiaries(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM apiaries")
        apiaries = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return apiaries
    
    def get_user_apiaries(self, user_id):
        """Gets all apiaries for a user"""
        return self.model.get_by_user(self.db, user_id)
    
    def update_apiary(self, apiary_id, **kwargs):
        """Updates apiary information"""
        self.model.update(self.db, apiary_id, **kwargs)
    
    def delete_apiary(self, apiary_id):
        """Deletes an apiary"""
        self.model.delete(self.db, apiary_id)
