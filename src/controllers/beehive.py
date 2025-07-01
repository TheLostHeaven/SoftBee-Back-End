from src.models.hive import HiveModel

class HiveController:
    def __init__(self, db):
        self.db = db
        self.model = HiveModel
    
    def create_hive(self, apiary_id, hive_number, **kwargs):
        if self.model.get_hive_number(self.db, apiary_id, hive_number):
            raise ValueError("Hive number already exists in this apiary")
        return self.model.create(self.db, apiary_id, hive_number, **kwargs)
    
    def get_hive(self, hive_id):
        return self.model.get_by_id(self.db, hive_id)
    
    def get_apiary_hives(self, apiary_id):
        return self.model.get_by_apiary(self.db, apiary_id)
    
    def update_hive(self, hive_id, **kwargs):
        if 'hive_number' in kwargs:
            hive = self.get_hive(hive_id)
            if not hive:
                raise ValueError("Hive not found")
            hive = dict(hive)
            
            existing = self.model.get_hive_number(self.db, hive['apiary_id'], kwargs['hive_number'])
            if existing and existing['id'] != hive_id:
                raise ValueError("Hive number already exists in this apiary")
        
        self.model.update(self.db, hive_id, **kwargs)
    
    def delete_hive(self, hive_id):
        self.model.delete(self.db, hive_id)
    
    def get_hive_by_number(self, apiary_id, hive_number):
        return self.model.get_hive_number(self.db, apiary_id, hive_number)
