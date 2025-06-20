from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
from ..models.users import UserModel

class UserController:
    def __init__(self, db):
        self.db = db
        self.model = UserModel

    def create_user(self, nombre, username, email, phone, password):
        """Creates a new user with hashed password"""
        hashed_password = generate_password_hash(password)
        return self.model.create(self.db, nombre, username, email, phone, hashed_password)


    def get_user(self, user_id):
        """Gets user by ID"""
        return self.model.get_by_id(self.db, user_id)

    def get_all_users(self):
        """Returns all users"""
        return self.model.get_all(self.db)

    def update_user(self, user_id, **kwargs):
        """Updates user information"""
        if 'password' in kwargs:
            kwargs['password'] = generate_password_hash(kwargs['password'])
        self.model.update(self.db, user_id, **kwargs)

    def delete_user(self, user_id):
        """Deletes a user"""
        self.model.delete(self.db, user_id)


