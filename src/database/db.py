# src/database/db.py
import sqlite3
import os
from flask import g, current_app
from src.models.users import UserModel
from src.models.apiary import ApiaryModel
from src.models.beehive import BeehiveModel
from src.models.inspection import InspectionModel
from src.models.apiary_access import ApiaryAccessModel
from src.models.questions import QuestionModel
from src.models.inventory import InventoryModel

def get_db():
    """Obtiene o crea una conexión a la base de datos"""
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        
        init_database(g.db)
    return g.db

def close_db(e=None):
    """Cierra la conexión a la base de datos si existe"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_database(db):
    """Inicializa todas las tablas en la base de datos"""
    UserModel.init_db(db)
    ApiaryModel.init_db(db)
    BeehiveModel.init_db(db)
    InspectionModel.init_db(db)
    ApiaryAccessModel.init_db(db)
    QuestionModel.init_db(db)
    InventoryModel.init_db(db)
    db.commit()

def init_app(app):
    """Registra las funciones con la aplicación Flask"""
    app.teardown_appcontext(close_db)
    
    with app.app_context():
        db = get_db()
        init_database(db)