import jwt
from datetime import datetime, timezone
from config import jwtKey, expiresTokenSession, algorithm

def generate_token(user_id, user_data):

    payload = {
        'user_id': user_id,
        'username': user_data['username'],  # Accedemos como diccionario
        'exp': datetime.now(timezone.utc).timestamp() + expiresTokenSession
    }
    
    return jwt.encode(payload, jwtKey, algorithm=algorithm)