from ..models.apiary import ApiaryModel
from ..models.users import UserModel

class ApiaryController:
    def __init__(self, db):
        self.db = db
        self.model = ApiaryModel
    
    def create_apiary(self, user_id, name, location=None):
        # Verifica que el usuario exista antes de crear el apiario
        user = UserModel.get_by_id(self.db, user_id)
        if not user:
            return None
        return self.model.create(self.db, user_id, name, location)

    def get_apiary(self, apiary_id):
        return self.model.get_by_id(self.db, apiary_id)

    def get_all_apiaries_for_user(self, user_id):
        # Solo retorna apiarios si el usuario existe
        user = UserModel.get_by_id(self.db, user_id)
        if not user:
            return None
        return self.model.get_by_user(self.db, user_id)

    def update_apiary(self, apiary_id, **kwargs):
        # Solo permite actualizar si el apiario existe y pertenece a un usuario existente
        apiary = self.model.get_by_id(self.db, apiary_id)
        if not apiary:
            return False
        user = UserModel.get_by_id(self.db, apiary['user_id'])
        if not user:
            return False
        self.model.update(self.db, apiary_id, **kwargs)
        return True

    def delete_apiary(self, apiary_id):
        # Solo permite eliminar si el apiario existe y pertenece a un usuario existente
        apiary = self.model.get_by_id(self.db, apiary_id)
        if not apiary:
            return False
        user = UserModel.get_by_id(self.db, apiary['user_id'])
        if not user:
            return False
        self.model.delete(self.db, apiary_id)
        return True
