import os
from flask import g, current_app
import psycopg2

def get_db():
    if 'db' not in g:
        # Usa DATABASE_URL si está definida, si no usa una conexión local por defecto
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            # Configuración local por defecto (ajusta usuario, contraseña y base de datos según tu entorno)
            user = os.getenv('PGUSER', 'postgres')
            password = os.getenv('PGPASSWORD', 'postgres')
            host = os.getenv('PGHOST', 'localhost')
            port = os.getenv('PGPORT', '5432')
            dbname = os.getenv('PGDATABASE', 'softbee')
            database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        g.db = psycopg2.connect(
            database_url,
            sslmode='require'  # Solo descomenta si necesitas SSL en producción
        )
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