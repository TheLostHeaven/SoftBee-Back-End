import bcrypt
from datetime import datetime, timedelta
import secrets
from ..models.users import UserModel

class UserController:
    def __init__(self, db):
        self.db = db
        self.model = UserModel

    def create_user(self, nombre, username, email, phone, password, profile_picture=None):
        """Creates a new user, apiary and empty inventory"""
        from ..controllers.apiary import ApiaryController
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_id = self.model.create(self.db, nombre, username, email, phone, hashed_password, profile_picture)
        # Crear apiario automáticamente con el nombre del usuario
        apiary_controller = ApiaryController(self.db)
        apiary_controller.create_apiary(user_id, nombre)
        return user_id


    def get_user(self, user_id):
        """Gets user by ID"""
        return self.model.get_by_id(self.db, user_id)

    def get_all_users(self):
        """Returns all users"""
        return self.model.get_all(self.db)

    def update_user(self, user_id, **kwargs):
        """Updates user information"""
        if 'password' in kwargs:
            kwargs['password'] = bcrypt.hashpw(kwargs['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.model.update(self.db, user_id, **kwargs)

    def delete_user(self, user_id):
        """Deletes a user"""
        self.model.delete(self.db, user_id)

    def update_profile_picture(self, user_id, filename):
        """Updates user's profile picture"""
        self.model.update_profile_picture(self.db, user_id, filename)

