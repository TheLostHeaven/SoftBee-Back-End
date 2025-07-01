import psycopg2
import psycopg2.extras
import json
from datetime import datetime

class QuestionModel:
    @staticmethod
    def init_db(db):
        cursor = db.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id SERIAL PRIMARY KEY,
                    apiary_id INTEGER NOT NULL,
                    external_id TEXT,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL CHECK (question_type IN ('texto', 'numero', 'opciones', 'rango')),
                    category VARCHAR(100),
                    is_required BOOLEAN NOT NULL DEFAULT FALSE,
                    display_order INTEGER NOT NULL,
                    min_value INTEGER,
                    max_value INTEGER,
                    options JSONB,
                    depends_on TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_apiary ON questions (apiary_id)')
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def _execute_query(db, query, params=()):
        cursor = db.cursor()
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    @staticmethod
    def _execute_update(db, query, params=()):
        cursor = db.cursor()
        try:
            cursor.execute(query, params)
            db.commit()
            return cursor
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def create(db, apiary_id, question_text, question_type, category=None, is_required=False,
               display_order=0, min_value=None, max_value=None, options=None, 
               depends_on=None, is_active=True, external_id=None):
        cursor = db.cursor()
        try:
            cursor.execute(
                '''
                INSERT INTO questions 
                (apiary_id, external_id, question_text, question_type, category, is_required, display_order, 
                min_value, max_value, options, depends_on, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                ''',
                (apiary_id, external_id, question_text, question_type, category, is_required, display_order,
                 min_value, max_value, json.dumps(options) if options else None, depends_on, is_active)
            )
            question_id = cursor.fetchone()[0]
            db.commit()
            return question_id
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(db, question_id):
        results = QuestionModel._execute_query(
            db,
            'SELECT * FROM questions WHERE id = %s',
            (question_id,)
        )
        return results[0] if results else None

    @staticmethod
    def get_by_apiary(db, apiary_id, active_only=True):
        query = '''
            SELECT * 
            FROM questions 
            WHERE apiary_id = %s 
                {}
            ORDER BY display_order
        '''.format("AND is_active = TRUE" if active_only else "")
        params = (apiary_id,)
        return QuestionModel._execute_query(db, query, params)

    @staticmethod
    def update(db, question_id, **kwargs):
        if not kwargs:
            raise ValueError("No fields to update")

        # Explicitly handle options serialization
        if 'options' in kwargs:
            options_data = kwargs.pop('options')
            if options_data is not None:
                kwargs['options'] = json.dumps(options_data)
            else:
                kwargs['options'] = None

        kwargs.pop('id', None) # Prevent changing the ID
        
        # Filter out keys that are not columns in the table to be safe
        valid_fields = [
            'external_id', 'question_text', 'question_type', 'category', 
            'is_required', 'display_order', 'min_value', 'max_value', 
            'options', 'depends_on', 'is_active'
        ]
        
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}

        if not update_fields:
            raise ValueError("No valid fields to update")

        set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
        params = list(update_fields.values())
        params.append(question_id)

        query = f"""
            UPDATE questions 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """
        QuestionModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, question_id):
        QuestionModel._execute_update(
            db,
            'DELETE FROM questions WHERE id = %s',
            (question_id,)
        )

    @staticmethod
    def reorder(db, apiary_id, new_order):
        order_data = [(order, qid) for order, qid in enumerate(new_order, 1)]
        query = """
            UPDATE questions
            SET display_order = CASE id
                {}
            END
            WHERE apiary_id = %s AND id IN %s
        """.format("\n".join([f"WHEN %s THEN %s" for _ in order_data]))
        params = [item for pair in order_data for item in (pair[1], pair[0])]
        params.extend([apiary_id, tuple(new_order)])
        QuestionModel._execute_update(db, query, params)

    @staticmethod
    def get_by_external_id(db, apiary_id, external_id):
        results = QuestionModel._execute_query(
            db,
            '''SELECT * FROM questions WHERE apiary_id = %s AND external_id = %s''',
            (apiary_id, external_id)
        )
        return results[0] if results else None

    @staticmethod
    def insert_or_update_default_question(db, apiary_id, external_id, question_text, question_type, category, is_required, display_order, min_value, max_value, options, depends_on, is_active):
        existing_question = QuestionModel.get_by_external_id(db, apiary_id, external_id)
        if existing_question:
            update_fields = {
                'question_text': question_text,
                'question_type': question_type,
                'category': category,
                'is_required': is_required,
                'display_order': display_order,
                'min_value': min_value,
                'max_value': max_value,
                'options': json.dumps(options) if options else None,
                'depends_on': depends_on,
                'is_active': is_active
            }
            QuestionModel.update(db, existing_question['id'], **update_fields)
            return existing_question['id']
        else:
            return QuestionModel.create(
                db, apiary_id, question_text, question_type, category, is_required,
                display_order, min_value, max_value, options, depends_on, is_active, external_id
            )
