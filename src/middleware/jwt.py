from flask import request, current_app, g
import jwt
from datetime import datetime, timedelta
from functools import wraps

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Obtener token de los headers
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return {'error': 'Token is missing'}, 401
        
        # Verificar token
        payload = verify_token(token)
        if not payload:
            return {'error': 'Invalid or expired token'}, 401
        
        # Almacenar información del usuario en el contexto global
        g.current_user_id = payload['sub']
        return f(*args, **kwargs)
    return decorated_function

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