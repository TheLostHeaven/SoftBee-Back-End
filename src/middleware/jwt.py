from flask import current_app
import jwt
from datetime import datetime, timedelta

def generate_token(user_id, user_data=None):
    """Genera un token JWT"""
    payload = {
        'sub': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(
            minutes=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
        )
    }
    if user_data:
        payload.update(user_data)
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )

def verify_token(token):
    """Verifica un token JWT"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=[current_app.config['JWT_ALGORITHM']]
        )
        return payload
    except jwt.ExpiredSignatureError:
        current_app.logger.warning("Token JWT expirado")
        return None
    except jwt.InvalidTokenError:
        current_app.logger.warning("Token JWT inválido")
        return None