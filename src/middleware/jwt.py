from flask import request, current_app, g, jsonify
import jwt
from datetime import datetime, timedelta
from functools import wraps

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 1. Obtener token de los headers
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(" ")[1]
        
        if not token:
            current_app.logger.error("Acceso no autorizado: Token no proporcionado")
            return jsonify({
                'success': False,
                'error': 'Token de autorización requerido',
                'code': 'token_missing'
            }), 401
        
        try:
            # 2. Verificar token
            current_app.logger.debug(f"Verificando token: {token[:15]}...")  # Log parcial por seguridad
            
            # Decodificar el token
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=[current_app.config['JWT_ALGORITHM']]
            )
            
            # 3. Verificar expiración
            now = datetime.utcnow().timestamp()
            if 'exp' not in payload or payload['exp'] < now:
                current_app.logger.warning(
                    f"Token expirado. Expiración: {payload.get('exp')}, "
                    f"Ahora: {now}"
                )
                return jsonify({
                    'success': False,
                    'error': 'Token expirado',
                    'code': 'token_expired',
                    'expired_at': payload.get('exp'),
                    'current_time': now
                }), 401
            
            # 4. Verificar sujeto (sub)
            if 'sub' not in payload:
                current_app.logger.warning("Token inválido: Falta campo 'sub'")
                return jsonify({
                    'success': False,
                    'error': 'Token inválido',
                    'code': 'token_invalid',
                    'details': "Falta campo 'sub' en el token"
                }), 401
            
            g.current_user_id = int(payload['sub']) 
            g.current_user_token = token 
            g.current_user_payload = payload  
            
            current_app.logger.debug(
                f"Token válido para usuario: {g.current_user_id}"
            )
            
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token JWT expirado (ExpiredSignatureError)")
            return jsonify({
                'success': False,
                'error': 'Token expirado',
                'code': 'token_expired'
            }), 401
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Token JWT inválido: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Token inválido',
                'code': 'token_invalid',
                'details': str(e)
            }), 401
        except Exception as e:
            current_app.logger.error(f"Error inesperado al verificar token: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'code': 'server_error'
            }), 500
            
    return decorated_function

def generate_token(user_id, user_data=None):
    """Genera un token JWT"""
    try:
        payload = {
            'sub': str(user_id),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(
                minutes=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
            )
        }
        
        if user_data:
            payload.update(user_data)
        
        current_app.logger.debug(f"Generando token para usuario: {user_id}")
        
        token = jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm=current_app.config['JWT_ALGORITHM']
        )
        
        return token
        
    except Exception as e:
        current_app.logger.error(f"Error al generar token: {str(e)}")
        raise

def verify_token(token):
    """Verifica un token JWT y devuelve el payload si es válido"""
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
    except jwt.InvalidTokenError as e:
        current_app.logger.warning(f"Token JWT inválido: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"Error al verificar token: {str(e)}")
        return None