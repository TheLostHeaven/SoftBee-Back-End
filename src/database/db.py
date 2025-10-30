"""
Configuración de base de datos con soporte para migraciones
Este archivo mantiene la compatibilidad con el sistema actual pero agrega soporte para SQLAlchemy y Flask-Migrate
"""

import os
import sqlite3
from flask import g, current_app
import psycopg2
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

# Instancia global de SQLAlchemy para migraciones
db = SQLAlchemy()
migrate = Migrate()

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
    """Inicializa la base de datos con la aplicación Flask"""
    
    # Configurar SQLAlchemy para migraciones
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar SQLAlchemy y Flask-Migrate
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Mantener el sistema actual para compatibilidad
    app.teardown_appcontext(close_db)

    with app.app_context():
        # Importar modelos para que Flask-Migrate los detecte
        from src.models.sqlalchemy_models import (
            User, PasswordResetToken, Apiary, ApiaryAccess, 
            Hive, Inspection, Inventory, Question, Monitoreo
        )
        
        # Mostrar información del entorno y base de datos
        env = os.getenv('FLASK_ENV', 'local')
        config_name = app.config.__class__.__name__
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        print(f"🚀 Iniciando aplicación en entorno: {env}")
        print(f"⚙️  Configuración activa: {config_name}")
        
        if db_uri.startswith('sqlite'):
            db_type = 'SQLite'
            db_path = db_uri.replace('sqlite:///', '')
            print(f" Usando base de datos: {db_type}")
            print(f"📁 Archivo SQLite: {db_path}")
        elif db_uri.startswith('postgresql'):
            db_type = 'PostgreSQL'
            # Ocultar credenciales en la URL para seguridad
            safe_uri = db_uri.split('@')[-1] if '@' in db_uri else db_uri
            print(f"📂 Usando base de datos: {db_type}")
            print(f"🔗 Servidor PostgreSQL: {safe_uri.split('/')[0]}")
        else:
            print(f"🚀 Iniciando aplicación en entorno: {env}")
            print(f"📂 Usando base de datos: desconocida")
            
        print(f"🌐 URLs configuradas:")
        print(f"   Frontend: {app.config.get('FRONTEND_URL')}")
        print(f"   Backend: {app.config.get('BASE_URL')}")
        print(f"🐛 Debug mode: {app.config.get('DEBUG', False)}")

        # Solo crear tablas automáticamente si no existen migraciones
        migrations_dir = os.path.join(app.root_path, '..', 'migrations')
        if not os.path.exists(migrations_dir):
            print("� No se encontraron migraciones, creando tablas automáticamente...")
            try:
                # Crear tablas usando el sistema actual para compatibilidad
                db_connection = get_db()
                
                from src.models.users import UserModel
                from src.models.password_reset_tokens import PasswordResetTokenModel
                from src.models.apiary import ApiaryModel
                from src.models.hive import HiveModel
                from src.models.apiary_access import ApiaryAccessModel
                from src.models.questions import QuestionModel
                from src.models.inventory import InventoryModel
                from src.models.monitoreo import MonitoreoModel
                
                UserModel.init_db(db_connection)
                PasswordResetTokenModel.init_db(db_connection)
                ApiaryModel.init_db(db_connection)
                QuestionModel.init_db(db_connection)
                InventoryModel.init_db(db_connection)
                HiveModel.init_db(db_connection)
                ApiaryAccessModel.init_db(db_connection)
                MonitoreoModel.init_db(db_connection)
                print("✅ Tablas de base de datos inicializadas correctamente")
            except Exception as e:
                print(f"❌ Error al inicializar tablas: {e}")
                raise
        else:
            print("📋 Migraciones encontradas, usar 'flask db upgrade' para aplicar cambios")