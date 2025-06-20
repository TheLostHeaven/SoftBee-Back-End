import sqlite3
import os
from flask import g, current_app

def get_db():
    """Obtiene o crea una conexión a la base de datos"""
    if 'db' not in g:
        # Asegura que el directorio instance exista
        os.makedirs(current_app.instance_path, exist_ok=True)
        
        # Conecta a la base de datos con configuración para multihilo
        db_path = os.path.join(current_app.instance_path, 'app.db')
        g.db = sqlite3.connect(db_path, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        
    return g.db

def close_db(e=None):
    """Cierra la conexión a la base de datos si existe"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Registra las funciones con la aplicación Flask"""
    # Configura la ruta de la base de datos
    app.config['DATABASE'] = os.path.join(app.instance_path, 'app.db')
    
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
        
        # Crea todas las tablas
        UserModel.init_db(db)
        ApiaryModel.init_db(db)
        QuestionModel.init_db(db)
        InventoryModel.init_db(db)
        BeehiveModel.init_db(db)
        InspectionModel.init_db(db)
        ApiaryAccessModel.init_db(db)
        db.commit()