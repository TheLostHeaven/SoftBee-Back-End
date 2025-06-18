# src/database/db.py
import sqlite3
import os
from flask import g, current_app
from src.models.users import init_users
from src.models.apiary import init_apiary
from src.models.beehive import init_beehive
from src.models.inspection import init_inspection
from src.models.apiary_access import init_apiary_access
from src.models.questions import QuestionModel

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
    init_users(db)
    init_apiary(db)
    init_beehive(db)
    init_inspection(db)
    init_apiary_access(db)
    QuestionModel.init_db(db)
    db.commit()

def init_app(app):
    """Registra las funciones con la aplicación Flask"""
    app.teardown_appcontext(close_db)
    
    with app.app_context():
        db = get_db()
        init_database(db)