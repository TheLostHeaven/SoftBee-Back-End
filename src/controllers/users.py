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

    def verify_user(self, username, password):
        """Verifies user credentials"""
        user = self.model.get_by_username(self.db, username)
        if user and check_password_hash(user['password'], password):
            return user
        return None

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

    def initiate_password_reset(self, email):
        """Initiates password reset process"""
        user = self.model.get_by_email(self.db, email)
        if not user:
            return None

        token = secrets.token_urlsafe(32)
        self.model.set_reset_token(self.db, email, token)
        return token

    def reset_password(self, token, new_password):
        """Resets password using valid token"""
        user = self.model.verify_reset_token(self.db, token)
        if not user:
            return False

        hashed_password = generate_password_hash(new_password)
        self.model.update_password(self.db, user['id'], hashed_password)
        return True
