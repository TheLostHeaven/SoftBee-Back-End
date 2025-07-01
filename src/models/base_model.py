# src/models/base_model.py
import sqlite3
from flask import current_app

class BaseModel:
    """Clase base con métodos comunes a todos los modelos"""
    
    @staticmethod
    def _execute_query(db, query, params=()):
        """Ejecuta una consulta de selección"""
        try:
            cursor = db.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            current_app.logger.error(f"Query error: {str(e)} - Query: {query}")
            raise

    @staticmethod
    def _execute_update(db, query, params=()):
        """Ejecuta una consulta de actualización"""
        try:
            cursor = db.execute(query, params)
            db.commit()
            return cursor
        except sqlite3.Error as e:
            db.rollback()
            current_app.logger.error(f"Update error: {str(e)} - Query: {query}")
            raise   