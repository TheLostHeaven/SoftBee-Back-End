import sqlite3
import os
from flask import g, current_app
import psycopg2

def get_db():
    if 'db' not in g:
        if 'RENDER' in os.environ:
            # PostgreSQL en producción
            g.db = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
        else:
            # SQLite en desarrollo
            g.db = sqlite3.connect('instance/database.db')
            g.db.row_factory = sqlite3.Row
    return g.db 




# def get_db():
#     """Obtiene o crea una conexión a la base de datos persistente"""
#     if 'db' not in g:
#         # Usamos /tmp que es persistente en Render
#         db_dir = '/tmp/beekeeper_db'  # Directorio especial para tu app
#         os.makedirs(db_dir, exist_ok=True)
        
#         db_path = os.path.join(db_dir, 'app.db')
        
#         g.db = sqlite3.connect(db_path, check_same_thread=False)
#         g.db.row_factory = sqlite3.Row
#         g.db.execute("PRAGMA foreign_keys = ON")
#         g.db.execute("PRAGMA journal_mode=WAL")
        
#     return g.db

def close_db(e=None):
    """Cierra la conexión a la base de datos si existe"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Registra las funciones con la aplicación Flask"""
    # Configura la ruta de la base de datos en /tmp
    app.config['DATABASE'] = '/tmp/beekeeper_db/app.db'
    
    # Registra la función de limpieza
    app.teardown_appcontext(close_db)
    
    # Inicializa la base de datos
    with app.app_context():
        db = get_db()
        # Importa y inicializa todos los modelos
        from src.models.users import UserModel
        from src.models.apiary import ApiaryModel
        from src.models.beehive import BeehiveModel
        from src.models.inspection import InspectionModel
        from src.models.apiary_access import ApiaryAccessModel
        from src.models.questions import QuestionModel
        from src.models.inventory import InventoryModel
        from src.models.password_reset_tokens import PasswordResetTokenModel
        
        # Crea todas las tablas
        UserModel.init_db(db)
        ApiaryModel.init_db(db)
        QuestionModel.init_db(db)
        InventoryModel.init_db(db)
        BeehiveModel.init_db(db)
        InspectionModel.init_db(db)
        ApiaryAccessModel.init_db(db)
        PasswordResetTokenModel.init_db(db)
        db.commit()