import os
from flask import g, current_app
import psycopg2
from urllib.parse import quote_plus  # Importa para codificar la contraseña

def get_db():
    if 'db' not in g:
        database_url = os.getenv('DATABASE_URL')
        sslmode_require = os.getenv('SSL_MODE', '') == 'require'

        if not database_url:
            # Configuración local
            user = os.getenv('PGUSER', 'postgres')
            password = os.getenv('PGPASSWORD', 'postgres')
            host = os.getenv('PGHOST', 'localhost')
            port = os.getenv('PGPORT', '5432')
            dbname = os.getenv('PGDATABASE', 'softbee')
            
            # Codifica la contraseña por si tiene caracteres especiales
            password_encoded = quote_plus(password)
            database_url = f"postgresql://{user}:{password_encoded}@{host}:{port}/{dbname}"
        else:
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # Agrega sslmode=require al URI si es necesario
        if sslmode_require and 'sslmode=' not in database_url:
            separator = '?' if '?' not in database_url else '&'
            database_url += f"{separator}sslmode=require"

        # Conexión SOLO con el URI (sin parámetros adicionales)
        g.db = psycopg2.connect(database_url)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)

    with app.app_context():
        db = get_db()
        

        from src.models.users import UserModel
        from src.models.password_reset_tokens import PasswordResetTokenModel
        from src.models.apiary import ApiaryModel
        from src.models.beehive import BeehiveModel
        # from src.models.inspection import InspectionModel
        from src.models.apiary_access import ApiaryAccessModel
        from src.models.questions import QuestionModel
        from src.models.inventory import InventoryModel
        from src.models.password_reset_tokens import PasswordResetTokenModel
        from src.models.monitoreo import MonitoreoModel
        
        # Crear tablas
        UserModel.init_db(db)
        PasswordResetTokenModel.init_db(db)
        ApiaryModel.init_db(db)
        QuestionModel.init_db(db)
        InventoryModel.init_db(db)
        BeehiveModel.init_db(db)
        # InspectionModel.init_db(db)
        ApiaryAccessModel.init_db(db)
        PasswordResetTokenModel.init_db(db)
        MonitoreoModel.init_db(db)