import sqlite3
import json

class QuestionModel:
    @staticmethod
    def init_db(db):
        try:
            db.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id TEXT PRIMARY KEY,
                    apiary_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL CHECK(question_type IN ('text', 'number', 'option')),
                    is_required BOOLEAN NOT NULL DEFAULT 0,
                    display_order INTEGER NOT NULL,
                    min_value INTEGER,
                    max_value INTEGER,
                    options TEXT,  -- JSON array for option questions
                    depends_on TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
                )
            ''')
            db.execute('CREATE INDEX IF NOT EXISTS idx_questions_apiary_id ON questions(apiary_id)')
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            raise e

    @staticmethod
    def _execute_query(db, query, params=()):
        return db.execute(query, params).fetchall()

    @staticmethod
    def _execute_update(db, query, params=()):
        cursor = db.execute(query, params)
        db.commit()
        return cursor

    @staticmethod
    def create(db, apiary_id, question_id, question_text, question_type, is_required=False, 
               display_order=0, min_value=None, max_value=None, options=None, depends_on=None, is_active=True):
        
        options_json = json.dumps(options) if options else None
        
        cursor = QuestionModel._execute_update(
            db,
            '''
            INSERT INTO questions 
            (apiary_id, id, question_text, question_type, is_required, display_order, 
             min_value, max_value, options, depends_on, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (apiary_id, question_id, question_text, question_type, int(is_required), display_order,
             min_value, max_value, options_json, depends_on, int(is_active))
        )
        return cursor.lastrowid

    @staticmethod
    def get_by_id(db, question_id):
        result = QuestionModel._execute_query(db, 'SELECT * FROM questions WHERE id = ?', (question_id,))
        if result:
            question = dict(result[0])
            if question['options']:
                question['options'] = json.loads(question['options'])
            return question
        return None

    @staticmethod
    def get_by_apiary(db, apiary_id, active_only=True):
        query = 'SELECT * FROM questions WHERE apiary_id = ?'
        params = [apiary_id]
        
        if active_only:
            query += ' AND is_active = 1'
        
        query += ' ORDER BY display_order'
        
        questions = QuestionModel._execute_query(db, query, params)
        processed = []
        for q in questions:
            question = dict(q)
            if question['options']:
                question['options'] = json.loads(question['options'])
            processed.append(question)
        return processed

    @staticmethod
    def update(db, question_id, **kwargs):
        if not kwargs:
            raise ValueError("No fields to update")
        
        fields = []
        params = []
        
        if 'options' in kwargs:
            kwargs['options'] = json.dumps(kwargs['options']) if kwargs['options'] else None
        
        for field, value in kwargs.items():
            fields.append(f"{field} = ?")
            params.append(value)
        
        params.append(question_id)
        query = f"UPDATE questions SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        QuestionModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, question_id):
        QuestionModel._execute_update(db, 'DELETE FROM questions WHERE id = ?', (question_id,))

    @staticmethod
    def reorder(db, apiary_id, new_order):
        """Updates display order for multiple questions"""
        try:
            db.execute('BEGIN TRANSACTION')
            for order, question_id in enumerate(new_order, 1):
                db.execute(
                    'UPDATE questions SET display_order = ? WHERE id = ? AND apiary_id = ?',
                    (order, question_id, apiary_id))
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            raise e
