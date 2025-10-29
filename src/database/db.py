import os
import sqlite3
from flask import g, current_app
import psycopg2
from urllib.parse import quote_plus

def get_db():
    if 'db' not in g:
        database_url = current_app.config.get('DATABASE_URL')
        
        if not database_url:
            raise ValueError("DATABASE_URL no está configurada")
        
        # Detectar tipo de base de datos
        if database_url.startswith('sqlite'):
            # Configuración para SQLite
            db_path = database_url.replace('sqlite:///', '')
            
            # Crear directorio si no existe
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
            g.db_type = 'sqlite'
            
        elif database_url.startswith('postgresql') or database_url.startswith('postgres'):
            # Configuración para PostgreSQL
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            
            # Agregar SSL si es necesario
            sslmode_require = os.getenv('SSL_MODE', '') == 'require'
            if sslmode_require and 'sslmode=' not in database_url:
                separator = '?' if '?' not in database_url else '&'
                database_url += f"{separator}sslmode=require"
            
            g.db = psycopg2.connect(database_url)
            g.db_type = 'postgresql'
        else:
            raise ValueError(f"Tipo de base de datos no soportado: {database_url}")
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)

    with app.app_context():
        db = get_db()
        
        # Mostrar información del entorno y base de datos
        env = os.getenv('FLASK_ENV')
        db_type = getattr(g, 'db_type', 'unknown')
        print(f"🚀 Iniciando aplicación en entorno: {env}")
        print(f"📂 Usando base de datos: {db_type}")
        
        if db_type == 'sqlite':
            db_path = app.config.get('DATABASE_URL', '').replace('sqlite:///', '')
            print(f"📁 Archivo SQLite: {db_path}")

        from src.models.users import UserModel
        from src.models.password_reset_tokens import PasswordResetTokenModel
        from src.models.apiary import ApiaryModel
        from src.models.hive import HiveModel
        # from src.models.inspection import InspectionModel
        from src.models.apiary_access import ApiaryAccessModel
        from src.models.questions import QuestionModel
        from src.models.inventory import InventoryModel
        from src.models.password_reset_tokens import PasswordResetTokenModel
        from src.models.monitoreo import MonitoreoModel
        
        # Crear tablas
        try:
            UserModel.init_db(db)
            PasswordResetTokenModel.init_db(db)
            ApiaryModel.init_db(db)
            QuestionModel.init_db(db)
            InventoryModel.init_db(db)
            HiveModel.init_db(db)
            # InspectionModel.init_db(db)
            ApiaryAccessModel.init_db(db)
            PasswordResetTokenModel.init_db(db)
            MonitoreoModel.init_db(db)
            print("✅ Tablas de base de datos inicializadas correctamente")
        except Exception as e:
            print(f"❌ Error al inicializar tablas: {e}")
            raise