# src/database/db.py
import sqlite3
import os
from flask import g, current_app
from src.models.users import init_users
from src.models.apiary import init_apiary
from src.models.beehive import init_beehive
from src.models.inspection import init_inspection
from src.models.apiary_access import init_apiary_access


def get_db():
    """Obtiene o crea una conexión a la base de datos"""
    if 'db' not in g:
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(current_app.config['DATABASE']), exist_ok=True)
        
        # Conectar a la base de datos
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        
        # Inicializar todas las tablas
        init_database(g.db)
    return g.db

def close_db(e=None):
    """Cierra la conexión a la base de datos"""
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
    db.commit()

def init_app(app):
    """Registra las funciones con la aplicación Flask y crea tablas al inicio"""
    app.teardown_appcontext(close_db)
    