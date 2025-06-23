import os
import json
from datetime import datetime

class QuestionModel:
    @staticmethod
    def init_db(db):
        """Inicializa la tabla de preguntas (compatible SQLite y PostgreSQL)"""
        cursor = db.cursor()
        try:
            cursor.execute ('''
                CREATE TABLE IF NOT EXISTS questions (
                    id TEXT PRIMARY KEY,
                    apiary_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL CHECK(question_type IN ('text', 'number', 'option')),
                    is_required BOOLEAN NOT NULL DEFAULT FALSE,
                    display_order INTEGER NOT NULL,
                    min_value INTEGER,
                    max_value INTEGER,
                    options TEXT,
                    depends_on TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
                )
            ''')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def _execute_query(db, query, params=()):
        """Ejecuta consultas con placeholders universales"""
        cursor = db.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def _execute_update(db, query, params=()):
        """Ejecuta actualizaciones con placeholders universales"""
        cursor = db.execute(query, params)
        if hasattr(db, 'commit'):
            db.commit()
        return cursor

    @staticmethod
    def create(db, apiary_id, question_id, question_text, question_type, is_required=False, 
            display_order=0, min_value=None, max_value=None, options=None, depends_on=None, is_active=True):
        """Crea una nueva pregunta (compatible)"""
        # Convertir valores booleanos para compatibilidad
        is_required_val = 1 if is_required and not 'postgresql' in os.environ.get('DATABASE_URL', '') else is_required
        is_active_val = 1 if is_active and not 'postgresql' in os.environ.get('DATABASE_URL', '') else is_active
        
        options_json = json.dumps(options) if options else None
        
        cursor = QuestionModel._execute_update(
            db,
            '''
            INSERT INTO questions 
            (apiary_id, id, question_text, question_type, is_required, display_order, 
            min_value, max_value, options, depends_on, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (apiary_id, question_id, question_text, question_type, is_required_val, display_order,
            min_value, max_value, options_json, depends_on, is_active_val)
        )
        
        # PostgreSQL no devuelve lastrowid para claves TEXT
        return question_id

    @staticmethod
    def get_by_id(db, question_id):
        """Obtiene pregunta por ID (compatible)"""
        result = QuestionModel._execute_query(
            db,
            'SELECT * FROM questions WHERE id = %s',
            (question_id,)
        )
        
        if result:
            question = dict(result[0])
            if question.get('options'):
                question['options'] = json.loads(question['options'])
            return question
        return None

    @staticmethod
    def get_by_apiary(db, apiary_id, active_only=True):
        """Obtiene preguntas por apiario (compatible)"""
        query = 'SELECT * FROM questions WHERE apiary_id = %s'
        params = [apiary_id]
        
        if active_only:
            query += ' AND is_active = %s'
            params.append(1 if not 'postgresql' in os.environ.get('DATABASE_URL', '') else True)
        
        query += ' ORDER BY display_order'
        
        questions = QuestionModel._execute_query(db, query, params)
        processed = []
        for q in questions:
            question = dict(q)
            if question.get('options'):
                question['options'] = json.loads(question['options'])
            processed.append(question)
        return processed

    @staticmethod
    def update(db, question_id, **kwargs):
        """Actualiza pregunta (compatible)"""
        if not kwargs:
            raise ValueError("No fields to update")
        
        fields = []
        params = []
        
        if 'options' in kwargs:
            kwargs['options'] = json.dumps(kwargs['options']) if kwargs['options'] else None
        
        for field, value in kwargs.items():
            # Convertir booleanos para SQLite
            if field in ('is_required', 'is_active') and not 'postgresql' in os.environ.get('DATABASE_URL', ''):
                value = 1 if value else 0
                
            fields.append(f"{field} = %s")
            params.append(value)
        
        params.append(question_id)
        query = f"UPDATE questions SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
        QuestionModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, question_id):
        """Elimina pregunta (compatible)"""
        QuestionModel._execute_update(db, 'DELETE FROM questions WHERE id = %s', (question_id,))

    @staticmethod
    def reorder(db, apiary_id, new_order):
        """Actualiza orden de visualización (compatible)"""
        try:
            # Iniciar transacción
            if 'postgresql' in os.environ.get('DATABASE_URL', ''):
                db.execute('BEGIN')
            else:
                db.execute('BEGIN TRANSACTION')
                
            for order, question_id in enumerate(new_order, 1):
                db.execute(
                    'UPDATE questions SET display_order = %s WHERE id = %s AND apiary_id = %s',
                    (order, question_id, apiary_id))
                
            if hasattr(db, 'commit'):
                db.commit()
                
        except Exception as e:
            if hasattr(db, 'rollback'):
                db.rollback()
            raise e