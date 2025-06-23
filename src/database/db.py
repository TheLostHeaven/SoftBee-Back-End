import os
from flask import g, current_app
import psycopg2
import sqlite3

def get_db():
    if 'db' not in g:
        # Entorno de producción (Render)
        if 'RENDER' in os.environ:
            database_url = os.getenv('DATABASE_URL')
            
            # Corrección para formato de Render
            if database_url and database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            
            g.db = psycopg2.connect(
                database_url,
                sslmode='require'  # SSL obligatorio en Render
            )
        # Entorno de desarrollo (SQLite)
        else:
            g.db = sqlite3.connect(
                os.path.join(current_app.instance_path, 'softbee.sqlite'),
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
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
        from src.models.inspection import InspectionModel
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
        InspectionModel.init_db(db)
        ApiaryAccessModel.init_db(db)
        PasswordResetTokenModel.init_db(db)
        
        if not 'RENDER' in os.environ:
            db.commit()