from functools import wraps
from flask import request, jsonify, current_app
from config import secretKey,algorithm
import jwt
from src.models.users import UserModel

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Si estamos en un entorno de prueba, permitimos el paso sin verificar el token
        if current_app.config.get('TESTING'):
            return f(None, *args, **kwargs)
        
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config[secretKey], algorithms=[algorithm])
            current_user = UserModel.query.filter_by(username=data['username']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated