from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
from ..models.users import UserModel


class AuthController:
    def __init__(self, db):
        self.db = db

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