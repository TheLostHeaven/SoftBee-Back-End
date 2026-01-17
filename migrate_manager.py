#!/usr/bin/env python3
"""
Script para manejar migraciones de manera más sencilla
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuración forzada para evitar conflictos
os.environ['FLASK_ENV'] = 'local'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Configuración mínima de Flask
app = Flask(__name__)

# Configuración PostgreSQL para migraciones
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/softbee_migrations")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importar todos los modelos SQLAlchemy
with app.app_context():
    from src.models.sqlalchemy_models import *

if __name__ == '__main__':
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/softbee_migrations")
    print(f"Base de datos de migraciones: {db_url}")
    print("Para inicializar migraciones: python migrate_manager.py init")
    print("Para crear migración: python migrate_manager.py migrate 'mensaje'")
    print("Para aplicar migraciones: python migrate_manager.py upgrade")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            from flask_migrate import init
            with app.app_context():
                init()
                print("✅ Migraciones inicializadas")
        elif sys.argv[1] == 'migrate':
            message = sys.argv[2] if len(sys.argv) > 2 else 'Auto migration'
            from flask_migrate import migrate as migrate_func
            with app.app_context():
                migrate_func(message=message)
                print(f"✅ Migración creada: {message}")
        elif sys.argv[1] == 'upgrade':
            from flask_migrate import upgrade
            with app.app_context():
                upgrade()
                print("✅ Migraciones aplicadas")
        elif sys.argv[1] == 'current':
            from flask_migrate import current
            with app.app_context():
                revision = current()
                print(f"Revisión actual: {revision}")
        elif sys.argv[1] == 'history':
            from flask_migrate import history
            with app.app_context():
                history()
    else:
        app.run(debug=True)