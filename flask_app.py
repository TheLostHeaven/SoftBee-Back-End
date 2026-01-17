#!/usr/bin/env python3
"""
Script de Flask CLI para manejar migraciones
Este archivo permite usar comandos como 'flask db init', 'flask db migrate', etc.
"""

import os
from flask.cli import FlaskGroup
from app import create_app

os.environ['FLASK_ENV'] = 'local'

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)