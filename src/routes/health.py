"""
Rutas para verificar el estado de la aplicación y base de datos
Incluye endpoints de prueba para crear usuarios
"""

from flask import Blueprint, jsonify, current_app, request
from src.database.db import get_db
from src.controllers.users import UserController
import os
import random
from datetime import datetime

def create_health_routes():
    health_bp = Blueprint('health', __name__)

    @health_bp.route('/health', methods=['GET'])
    def health_check():
        """
        Endpoint para verificar el estado general de la aplicación
        """
        try:
            return jsonify({
                "status": "ok",
                "message": "SoftBee API está funcionando correctamente",
                "timestamp": datetime.now().isoformat(),
                "environment": os.getenv('FLASK_ENV', 'local')
            }), 200
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error en health check: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/health/db', methods=['GET'])
    def database_health_check():
        """
        Endpoint para verificar específicamente la conexión a la base de datos
        """
        try:
            # Obtener información de configuración
            database_url = current_app.config.get('DATABASE_URL')
            env = os.getenv('FLASK_ENV', 'local')
            
            if not database_url:
                return jsonify({
                    "status": "error",
                    "message": "DATABASE_URL no configurada",
                    "timestamp": datetime.now().isoformat(),
                    "environment": env
                }), 500

            # Probar conexión a la base de datos
            db_connection = get_db()
            
            # Detectar tipo de base de datos y hacer una consulta simple
            if database_url.startswith('sqlite'):
                cursor = db_connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                
                db_info = {
                    "type": "SQLite",
                    "path": database_url.replace('sqlite:///', ''),
                    "file_exists": os.path.exists(database_url.replace('sqlite:///', ''))
                }
                
            elif database_url.startswith('postgresql') or database_url.startswith('postgres'):
                cursor = db_connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                
                # Información segura de PostgreSQL (sin credenciales)
                safe_uri = database_url.split('@')[-1] if '@' in database_url else database_url
                db_info = {
                    "type": "PostgreSQL",
                    "server": safe_uri.split('/')[0] if '/' in safe_uri else safe_uri
                }
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Tipo de base de datos no soportado: {database_url[:10]}...",
                    "timestamp": datetime.now().isoformat(),
                    "environment": env
                }), 500

            return jsonify({
                "status": "ok",
                "message": "Conexión a base de datos exitosa",
                "timestamp": datetime.now().isoformat(),
                "environment": env,
                "database": db_info,
                "test_query_result": "Conexión verificada correctamente"
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error de conexión a base de datos: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "environment": os.getenv('FLASK_ENV', 'local'),
                "database_url_configured": current_app.config.get('DATABASE_URL') is not None
            }), 500

    @health_bp.route('/health/tables', methods=['GET'])
    def tables_health_check():
        """
        Endpoint para verificar las tablas existentes en la base de datos
        """
        try:
            database_url = current_app.config.get('DATABASE_URL')
            db_connection = get_db()
            tables = []
            
            if database_url.startswith('sqlite'):
                cursor = db_connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                cursor.close()
                
            elif database_url.startswith('postgresql') or database_url.startswith('postgres'):
                cursor = db_connection.cursor()
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
                tables = [row[0] for row in cursor.fetchall()]
                cursor.close()

            return jsonify({
                "status": "ok",
                "message": "Consulta de tablas exitosa",
                "timestamp": datetime.now().isoformat(),
                "environment": os.getenv('FLASK_ENV', 'local'),
                "tables_count": len(tables),
                "tables": sorted(tables)
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al consultar tablas: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "environment": os.getenv('FLASK_ENV', 'local')
            }), 500

    @health_bp.route('/health/config', methods=['GET'])
    def config_health_check():
        """
        Endpoint para verificar la configuración de la aplicación
        """
        try:
            config_info = {
                "environment": os.getenv('FLASK_ENV', 'local'),
                "debug_mode": current_app.config.get('DEBUG', False),
                "testing_mode": current_app.config.get('TESTING', False),
                "database_configured": current_app.config.get('DATABASE_URL') is not None,
                "frontend_url": current_app.config.get('FRONTEND_URL'),
                "base_url": current_app.config.get('BASE_URL'),
                "mail_configured": bool(current_app.config.get('MAIL_SERVER')),
                "config_class": current_app.config.__class__.__name__
            }

            return jsonify({
                "status": "ok",
                "message": "Configuración verificada",
                "timestamp": datetime.now().isoformat(),
                "config": config_info
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al verificar configuración: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/create-user', methods=['POST'])
    def test_create_user():
        """
        Endpoint para crear un usuario de prueba (Compatible con SQLite y PostgreSQL)
        """
        try:
            # Obtener datos del request o usar valores por defecto
            data = request.get_json() if request.is_json else {}
            
            # Generar datos aleatorios si no se proporcionan
            random_num = random.randint(1000, 9999)
            default_data = {
                "nombre": f"Usuario Test {random_num}",
                "username": f"testuser{random_num}",
                "email": f"test{random_num}@ejemplo.com",
                "phone": f"555-{random_num}",
                "password": "password123"
            }
            
            # Usar datos proporcionados o valores por defecto
            user_data = {
                "nombre": data.get("nombre", default_data["nombre"]),
                "username": data.get("username", default_data["username"]),
                "email": data.get("email", default_data["email"]),
                "phone": data.get("phone", default_data["phone"]),
                "password": data.get("password", default_data["password"])
            }
            
            # Validar campos requeridos
            required_fields = ['nombre', 'username', 'email', 'phone', 'password']
            if not all(field in user_data and user_data[field] for field in required_fields):
                return jsonify({
                    "status": "error",
                    "message": "Faltan campos requeridos",
                    "required_fields": required_fields,
                    "timestamp": datetime.now().isoformat()
                }), 400
            
            # Crear usuario directamente con SQL compatible
            from flask import g
            import bcrypt
            
            db_connection = get_db()
            db_type = getattr(g, 'db_type', 'sqlite')
            
            # Hash de la contraseña
            hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor = db_connection.cursor()
            
            try:
                if db_type == 'sqlite':
                    cursor.execute(
                        '''
                        INSERT INTO users (nombre, username, email, phone, password, profile_picture)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''',
                        (user_data['nombre'], user_data['username'].lower(), user_data['email'].lower(), 
                         user_data['phone'], hashed_password, 'profile_picture.png')
                    )
                    user_id = cursor.lastrowid
                else:  # PostgreSQL
                    cursor.execute(
                        '''
                        INSERT INTO users (nombre, username, email, phone, password, profile_picture)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                        ''',
                        (user_data['nombre'], user_data['username'].lower(), user_data['email'].lower(), 
                         user_data['phone'], hashed_password, 'profile_picture.png')
                    )
                    user_id = cursor.fetchone()[0]
                
                db_connection.commit()
                cursor.close()
                
                # Crear apiario automáticamente (simplificado)
                cursor = db_connection.cursor()
                if db_type == 'sqlite':
                    cursor.execute(
                        '''
                        INSERT INTO apiaries (name, location, user_id)
                        VALUES (?, ?, ?)
                        ''',
                        (f"Apiario de {user_data['nombre']}", "Ubicación por defecto", user_id)
                    )
                else:  # PostgreSQL
                    cursor.execute(
                        '''
                        INSERT INTO apiaries (name, location, user_id)
                        VALUES (%s, %s, %s)
                        ''',
                        (f"Apiario de {user_data['nombre']}", "Ubicación por defecto", user_id)
                    )
                
                db_connection.commit()
                cursor.close()
                
                return jsonify({
                    "status": "ok",
                    "message": "Usuario de prueba creado exitosamente",
                    "timestamp": datetime.now().isoformat(),
                    "user": {
                        "id": user_id,
                        "nombre": user_data['nombre'],
                        "username": user_data['username'],
                        "email": user_data['email'],
                        "phone": user_data['phone']
                    },
                    "database_type": db_type,
                    "note": "Usuario y apiario creados automáticamente"
                }), 201
                
            except Exception as db_error:
                db_connection.rollback()
                cursor.close()
                raise db_error
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al crear usuario de prueba: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/users', methods=['GET'])
    def test_get_users():
        """
        Endpoint para listar usuarios de prueba (Compatible con SQLite y PostgreSQL)
        """
        try:
            from flask import g
            
            db_connection = get_db()
            db_type = getattr(g, 'db_type', 'sqlite')
            
            cursor = db_connection.cursor()
            cursor.execute('SELECT * FROM users ORDER BY id')
            
            # Obtener nombres de columnas
            if db_type == 'sqlite':
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                users = [dict(zip(columns, row)) for row in rows]
            else:  # PostgreSQL
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                users = [dict(zip(columns, row)) for row in rows]
            
            cursor.close()
            
            # Limpiar información sensible y formatear fechas
            safe_users = []
            for user in users:
                safe_user = {
                    "id": user.get("id"),
                    "nombre": user.get("nombre"),
                    "username": user.get("username"),
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                    "profile_picture": user.get("profile_picture"),
                    "created_at": str(user.get("created_at")) if user.get("created_at") else None,
                    "updated_at": str(user.get("updated_at")) if user.get("updated_at") else None
                }
                safe_users.append(safe_user)
            
            return jsonify({
                "status": "ok",
                "message": "Usuarios obtenidos exitosamente",
                "timestamp": datetime.now().isoformat(),
                "database_type": db_type,
                "users_count": len(safe_users),
                "users": safe_users
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al obtener usuarios: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/user/<int:user_id>', methods=['GET'])
    def test_get_user(user_id):
        """
        Endpoint para obtener un usuario específico por ID (Compatible con SQLite y PostgreSQL)
        """
        try:
            from flask import g
            
            db_connection = get_db()
            db_type = getattr(g, 'db_type', 'sqlite')
            
            cursor = db_connection.cursor()
            
            if db_type == 'sqlite':
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            else:  # PostgreSQL
                cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            
            row = cursor.fetchone()
            
            if not row:
                cursor.close()
                return jsonify({
                    "status": "error",
                    "message": f"Usuario con ID {user_id} no encontrado",
                    "timestamp": datetime.now().isoformat()
                }), 404
            
            # Convertir row a diccionario
            if db_type == 'sqlite':
                columns = [description[0] for description in cursor.description]
                user = dict(zip(columns, row))
            else:  # PostgreSQL
                columns = [col[0] for col in cursor.description]
                user = dict(zip(columns, row))
            
            cursor.close()
            
            # Limpiar información sensible
            safe_user = {
                "id": user.get("id"),
                "nombre": user.get("nombre"),
                "username": user.get("username"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "profile_picture": user.get("profile_picture"),
                "created_at": str(user.get("created_at")) if user.get("created_at") else None,
                "updated_at": str(user.get("updated_at")) if user.get("updated_at") else None
            }
            
            return jsonify({
                "status": "ok",
                "message": "Usuario obtenido exitosamente",
                "timestamp": datetime.now().isoformat(),
                "database_type": db_type,
                "user": safe_user
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al obtener usuario: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/create-sample-users', methods=['POST'])
    def test_create_sample_users():
        """
        Endpoint para crear múltiples usuarios de ejemplo
        """
        try:
            # Datos de usuarios de ejemplo
            sample_users = [
                {
                    "nombre": "María González",
                    "username": "maria_apicultura",
                    "email": "maria@softbee.com",
                    "phone": "555-0001",
                    "password": "password123"
                },
                {
                    "nombre": "Carlos Rodríguez",
                    "username": "carlos_miel",
                    "email": "carlos@softbee.com",
                    "phone": "555-0002",
                    "password": "password123"
                },
                {
                    "nombre": "Ana Martínez",
                    "username": "ana_colmenas",
                    "email": "ana@softbee.com",
                    "phone": "555-0003",
                    "password": "password123"
                }
            ]
            
            db = get_db()
            controller = UserController(db)
            created_users = []
            
            for user_data in sample_users:
                try:
                    user_id = controller.create_user(
                        user_data['nombre'],
                        user_data['username'],
                        user_data['email'],
                        user_data['phone'],
                        user_data['password']
                    )
                    created_users.append({
                        "id": user_id,
                        "nombre": user_data['nombre'],
                        "username": user_data['username'],
                        "email": user_data['email']
                    })
                except Exception as user_error:
                    # Si hay error (por ejemplo, usuario ya existe), continuar con el siguiente
                    created_users.append({
                        "error": f"Error creando {user_data['username']}: {str(user_error)}",
                        "username": user_data['username']
                    })
            
            return jsonify({
                "status": "ok",
                "message": f"Proceso completado. {len([u for u in created_users if 'id' in u])} usuarios creados exitosamente",
                "timestamp": datetime.now().isoformat(),
                "created_users": created_users,
                "total_attempted": len(sample_users)
            }), 201
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al crear usuarios de ejemplo: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/db-structure', methods=['GET'])
    def test_db_structure():
        """
        Endpoint para verificar la estructura de las tablas principales
        """
        try:
            from flask import g
            
            db_connection = get_db()
            db_type = getattr(g, 'db_type', 'sqlite')
            
            tables_info = {}
            
            # Información de tabla users
            cursor = db_connection.cursor()
            if db_type == 'sqlite':
                cursor.execute("PRAGMA table_info(users)")
                users_columns = cursor.fetchall()
                tables_info['users'] = {
                    "columns": [{"name": col[1], "type": col[2], "not_null": bool(col[3]), "primary_key": bool(col[5])} for col in users_columns]
                }
                
                # Contar usuarios
                cursor.execute("SELECT COUNT(*) FROM users")
                tables_info['users']['count'] = cursor.fetchone()[0]
                
                # Información de tabla apiaries
                cursor.execute("PRAGMA table_info(apiaries)")
                apiaries_columns = cursor.fetchall()
                tables_info['apiaries'] = {
                    "columns": [{"name": col[1], "type": col[2], "not_null": bool(col[3]), "primary_key": bool(col[5])} for col in apiaries_columns]
                }
                
                # Contar apiarios
                cursor.execute("SELECT COUNT(*) FROM apiaries")
                tables_info['apiaries']['count'] = cursor.fetchone()[0]
                
            else:  # PostgreSQL
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                    ORDER BY ordinal_position
                """)
                users_columns = cursor.fetchall()
                tables_info['users'] = {
                    "columns": [{"name": col[0], "type": col[1], "nullable": col[2], "default": col[3]} for col in users_columns]
                }
                
                cursor.execute("SELECT COUNT(*) FROM users")
                tables_info['users']['count'] = cursor.fetchone()[0]
            
            cursor.close()
            
            return jsonify({
                "status": "ok",
                "message": "Estructura de base de datos obtenida",
                "timestamp": datetime.now().isoformat(),
                "database_type": db_type,
                "tables": tables_info
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al obtener estructura: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/summary', methods=['GET'])
    def test_summary():
        """
        Endpoint que proporciona un resumen completo del sistema con ejemplos de uso
        """
        try:
            from flask import g
            
            db_connection = get_db()
            db_type = getattr(g, 'db_type', 'sqlite')
            
            # Contar registros en tablas principales
            cursor = db_connection.cursor()
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            
            # Contar apiarios
            cursor.execute("SELECT COUNT(*) FROM apiaries")
            apiaries_count = cursor.fetchone()[0]
            
            # Contar colmenas (hives)
            cursor.execute("SELECT COUNT(*) FROM hives")
            hives_count = cursor.fetchone()[0]
            
            cursor.close()
            
            # Información del sistema
            env = os.getenv('FLASK_ENV', 'local')
            config_class = current_app.config.__class__.__name__
            
            # Ejemplos de uso
            base_url = "http://127.0.0.1:5000/api"
            examples = {
                "health_checks": {
                    "basic_health": f"curl -X GET {base_url}/health",
                    "database_health": f"curl -X GET {base_url}/health/db",
                    "tables_check": f"curl -X GET {base_url}/health/tables",
                    "config_check": f"curl -X GET {base_url}/health/config"
                },
                "user_testing": {
                    "create_random_user": f"curl -X POST {base_url}/test/create-user -H 'Content-Type: application/json' -d '{{}}'",
                    "create_specific_user": f"curl -X POST {base_url}/test/create-user -H 'Content-Type: application/json' -d '{{\"nombre\":\"Test User\",\"username\":\"testuser\",\"email\":\"test@ejemplo.com\",\"phone\":\"555-1234\",\"password\":\"password123\"}}'",
                    "list_users": f"curl -X GET {base_url}/test/users",
                    "get_user_by_id": f"curl -X GET {base_url}/test/user/1",
                    "check_db_structure": f"curl -X GET {base_url}/test/db-structure"
                },
                "production_endpoints": {
                    "create_user": f"curl -X POST {base_url}/users -H 'Content-Type: application/json' -d '{{\"nombre\":\"User Name\",\"username\":\"username\",\"email\":\"user@email.com\",\"phone\":\"555-0000\",\"password\":\"password\"}}'",
                    "get_all_users": f"curl -X GET {base_url}/users",
                    "get_user": f"curl -X GET {base_url}/users/1",
                    "login": f"curl -X POST {base_url}/login -H 'Content-Type: application/json' -d '{{\"email\":\"user@email.com\",\"password\":\"password\"}}'"
                }
            }
            
            return jsonify({
                "status": "ok",
                "message": "SoftBee API - Resumen del sistema",
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "environment": env,
                    "config_class": config_class,
                    "database_type": db_type,
                    "debug_mode": current_app.config.get('DEBUG', False)
                },
                "database_stats": {
                    "users": users_count,
                    "apiaries": apiaries_count,
                    "hives": hives_count,
                    "total_tables": 9
                },
                "api_endpoints": {
                    "health_checks": 4,
                    "user_testing": 5,
                    "production_ready": "Multiple endpoints available"
                },
                "usage_examples": examples,
                "notes": [
                    "Los endpoints /api/test/* son para pruebas y desarrollo",
                    "Los endpoints de producción están en /api/users, /api/auth, etc.",
                    "La base de datos está funcionando correctamente",
                    "Se pueden crear usuarios con apiarios automáticamente"
                ]
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al generar resumen: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/fix-sqlite-tables', methods=['POST'])
    def fix_sqlite_tables():
        """
        Endpoint para corregir las tablas SQLite con sintaxis correcta
        """
        try:
            from flask import g
            
            db_connection = get_db()
            db_type = getattr(g, 'db_type', 'sqlite')
            
            if db_type != 'sqlite':
                return jsonify({
                    "status": "error",
                    "message": "Este endpoint solo funciona con SQLite",
                    "timestamp": datetime.now().isoformat()
                }), 400
            
            cursor = db_connection.cursor()
            
            # Primero, verificar si hay datos existentes
            cursor.execute("SELECT COUNT(*) FROM users")
            users_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM apiaries")
            apiaries_count = cursor.fetchone()[0]
            
            # Respaldo de datos existentes si los hay
            users_backup = []
            apiaries_backup = []
            
            if users_count > 0:
                cursor.execute("SELECT * FROM users")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                users_backup = [dict(zip(columns, row)) for row in rows]
            
            if apiaries_count > 0:
                cursor.execute("SELECT * FROM apiaries")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                apiaries_backup = [dict(zip(columns, row)) for row in rows]
            
            # Recrear tabla users con sintaxis correcta de SQLite
            cursor.execute("DROP TABLE IF EXISTS users_new")
            cursor.execute('''
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100) NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    password VARCHAR(200) NOT NULL,
                    profile_picture VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Recrear tabla apiaries con sintaxis correcta de SQLite
            cursor.execute("DROP TABLE IF EXISTS apiaries_new")
            cursor.execute('''
                CREATE TABLE apiaries_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    location VARCHAR(50),   
                    beehives_count INTEGER DEFAULT 0,
                    treatments BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users_new(id) ON DELETE CASCADE
                )
            ''')
            
            # Restaurar datos en las nuevas tablas
            restored_users = 0
            restored_apiaries = 0
            
            for user in users_backup:
                if user.get('nombre'):  # Solo restaurar usuarios válidos
                    cursor.execute('''
                        INSERT INTO users_new (nombre, username, email, phone, password, profile_picture, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user.get('nombre'),
                        user.get('username'),
                        user.get('email'),
                        user.get('phone'),
                        user.get('password'),
                        user.get('profile_picture'),
                        user.get('created_at'),
                        user.get('updated_at')
                    ))
                    restored_users += 1
            
            for apiary in apiaries_backup:
                if apiary.get('name'):  # Solo restaurar apiarios válidos
                    cursor.execute('''
                        INSERT INTO apiaries_new (user_id, name, location, beehives_count, treatments, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        apiary.get('user_id'),
                        apiary.get('name'),
                        apiary.get('location'),
                        apiary.get('beehives_count', 0),
                        apiary.get('treatments', False),
                        apiary.get('created_at'),
                        apiary.get('updated_at')
                    ))
                    restored_apiaries += 1
            
            # Reemplazar tablas originales
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS apiaries")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            cursor.execute("ALTER TABLE apiaries_new RENAME TO apiaries")
            
            # Crear índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)")
            
            db_connection.commit()
            cursor.close()
            
            return jsonify({
                "status": "ok",
                "message": "Tablas SQLite corregidas exitosamente",
                "timestamp": datetime.now().isoformat(),
                "backup_info": {
                    "users_backed_up": users_count,
                    "apiaries_backed_up": apiaries_count,
                    "users_restored": restored_users,
                    "apiaries_restored": restored_apiaries
                },
                "next_steps": "Ahora puedes crear usuarios y verás que los IDs se generan correctamente"
            }), 200
            
        except Exception as e:
            db_connection.rollback()
            return jsonify({
                "status": "error",
                "message": f"Error al corregir tablas: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/apiaries', methods=['GET'])
    def test_get_apiaries():
        """
        Endpoint para listar apiarios y verificar que tienen IDs correctos
        """
        try:
            from flask import g
            
            db_connection = get_db()
            db_type = getattr(g, 'db_type', 'sqlite')
            
            cursor = db_connection.cursor()
            cursor.execute('''
                SELECT a.*, u.nombre as user_name, u.username 
                FROM apiaries a 
                LEFT JOIN users u ON a.user_id = u.id 
                ORDER BY a.id
            ''')
            
            # Obtener nombres de columnas
            if db_type == 'sqlite':
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                apiaries = [dict(zip(columns, row)) for row in rows]
            else:  # PostgreSQL
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                apiaries = [dict(zip(columns, row)) for row in rows]
            
            cursor.close()
            
            # Formatear la respuesta
            formatted_apiaries = []
            for apiary in apiaries:
                formatted_apiary = {
                    "id": apiary.get("id"),
                    "user_id": apiary.get("user_id"),
                    "name": apiary.get("name"),
                    "location": apiary.get("location"),
                    "beehives_count": apiary.get("beehives_count"),
                    "treatments": apiary.get("treatments"),
                    "created_at": str(apiary.get("created_at")) if apiary.get("created_at") else None,
                    "updated_at": str(apiary.get("updated_at")) if apiary.get("updated_at") else None,
                    "user_info": {
                        "name": apiary.get("user_name"),
                        "username": apiary.get("username")
                    }
                }
                formatted_apiaries.append(formatted_apiary)
            
            return jsonify({
                "status": "ok",
                "message": "Apiarios obtenidos exitosamente",
                "timestamp": datetime.now().isoformat(),
                "database_type": db_type,
                "apiaries_count": len(formatted_apiaries),
                "apiaries": formatted_apiaries
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al obtener apiarios: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    @health_bp.route('/test/login', methods=['POST'])
    def test_login():
        """
        Endpoint de login compatible con SQLite para pruebas
        """
        try:
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400

            data = request.get_json()
            from flask import g
            import bcrypt
            
            # Obtener datos de entrada
            identifier = data.get('email', data.get('username', '')).strip().lower()
            password = data.get('password', '').strip()

            if not password:
                return jsonify({'error': 'Password is required'}), 400
                
            if not identifier:
                return jsonify({'error': 'Username or email is required'}), 400

            db_connection = get_db()
            db_type = getattr(g, 'db_type', 'sqlite')
            
            # Buscar usuario (compatible con SQLite)
            cursor = db_connection.cursor()
            user = None
            
            if '@' in identifier:
                # Buscar por email
                if db_type == 'sqlite':
                    cursor.execute('SELECT * FROM users WHERE email = ?', (identifier,))
                else:  # PostgreSQL
                    cursor.execute('SELECT * FROM users WHERE email = %s', (identifier,))
            else:
                # Buscar por username
                if db_type == 'sqlite':
                    cursor.execute('SELECT * FROM users WHERE username = ?', (identifier,))
                else:  # PostgreSQL
                    cursor.execute('SELECT * FROM users WHERE username = %s', (identifier,))
            
            row = cursor.fetchone()
            
            if row:
                # Convertir row a diccionario
                if db_type == 'sqlite':
                    columns = [description[0] for description in cursor.description]
                    user = dict(zip(columns, row))
                else:  # PostgreSQL
                    columns = [col[0] for col in cursor.description]
                    user = dict(zip(columns, row))
            
            cursor.close()

            if not user:
                return jsonify({
                    'error': 'Invalid credentials',
                    'message': 'User not found'
                }), 401

            # Verificar contraseña
            stored_password = user['password']
            password_match = False
            
            try:
                if stored_password and (stored_password.startswith('$2b$') or stored_password.startswith('$2a$')):
                    password_match = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
                else:
                    password_match = False
            except Exception as e:
                password_match = False
            
            if not password_match:
                return jsonify({
                    'error': 'Invalid credentials',
                    'message': 'Incorrect password'
                }), 401

            # Login exitoso - limpiar datos sensibles
            safe_user = {
                "id": user.get("id"),
                "nombre": user.get("nombre"),
                "username": user.get("username"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "profile_picture": user.get("profile_picture"),
                "created_at": str(user.get("created_at")) if user.get("created_at") else None,
                "updated_at": str(user.get("updated_at")) if user.get("updated_at") else None
            }

            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'timestamp': datetime.now().isoformat(),
                'database_type': db_type,
                'user': safe_user,
                'note': 'Este es un endpoint de prueba - usar /api/login para producción'
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error en login: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }), 500

    return health_bp