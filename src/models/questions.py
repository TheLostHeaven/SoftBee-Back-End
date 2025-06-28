import json
from datetime import datetime

class QuestionModel:
    @staticmethod
    def init_db(db):
        """Inicializa la tabla de preguntas para PostgreSQL"""
        cursor = db.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id TEXT PRIMARY KEY,
                    apiary_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL CHECK(question_type IN ('texto', 'numero', 'opciones', 'rango')),
                    is_required BOOLEAN NOT NULL DEFAULT FALSE,
                    display_order INTEGER NOT NULL,
                    min_value INTEGER,
                    max_value INTEGER,
                    options JSONB,
                    depends_on TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (apiary_id) REFERENCES apiaries(id) ON DELETE CASCADE
                )
            ''')

            # Crear índice para búsquedas por apiario
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_questions_apiary
                ON questions (apiary_id)
            ''')

            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def _execute_query(db, query, params=()):
        """Ejecuta consultas y retorna resultados como diccionarios"""
        cursor = db.cursor()
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        finally:
            cursor.close()

    @staticmethod
    def _execute_update(db, query, params=()):
        """Ejecuta actualizaciones y hace commit"""
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
    def create(db, apiary_id, question_id, question_text, question_type, is_required=False,
                display_order=0, min_value=None, max_value=None, options=None, depends_on=None, is_active=True):
        """Crea una nueva pregunta en PostgreSQL"""
        cursor = db.cursor()
        try:
            cursor.execute(
                '''
                INSERT INTO questions 
                (id, apiary_id, question_text, question_type, is_required, display_order, 
                min_value, max_value, options, depends_on, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                ''',
                (question_id, apiary_id, question_text, question_type, is_required, display_order,
                min_value, max_value, json.dumps(options) if options else None, depends_on, is_active)
            )
            db.commit()
            return cursor.fetchone()[0]
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(db, question_id):
        """Obtiene pregunta por ID"""
        results = QuestionModel._execute_query(
            db,
            'SELECT * FROM questions WHERE id = %s',
            (question_id,)
        )
        return results[0] if results else None

    @staticmethod
    def get_by_apiary(db, apiary_id, active_only=True):
        """Obtiene preguntas por apiario"""
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
        """Actualiza pregunta en PostgreSQL"""
        if not kwargs:
            raise ValueError("No fields to update")

        # Manejo especial para campo options
        if 'options' in kwargs:
            kwargs['options'] = json.dumps(kwargs['options']) if kwargs['options'] else None

        # Evitar la actualización de la clave primaria
        kwargs.pop('id', None)

        set_clause = ", ".join([
            f"{field} = %s"
            for field in kwargs.keys()
            if field != 'updated_at'  # Excluir updated_at ya que se maneja automáticamente
        ])

        if not set_clause:
            raise ValueError("No valid fields to update")

        params = list(kwargs.values())
        params.append(question_id)

        query = f"""
            UPDATE questions 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s
        """

        QuestionModel._execute_update(db, query, params)

    @staticmethod
    def delete(db, question_id):
        """Elimina pregunta"""
        QuestionModel._execute_update(
            db,
            'DELETE FROM questions WHERE id = %s',
            (question_id,)
        )

    @staticmethod
    def reorder(db, apiary_id, new_order):
        """Actualiza orden de visualización usando una única consulta eficiente"""
        # Crear una lista de tuplas (order, question_id)
        order_data = [(order, qid) for order, qid in enumerate(new_order, 1)]

        # Usar una consulta UPDATE con CASE para mayor eficiencia
        query = """
            UPDATE questions
            SET display_order = CASE id
                {}
            END
            WHERE apiary_id = %s AND id IN %s
        """.format(
            "\n".join([f"WHEN %s THEN %s" for _ in order_data])
        )

        # Preparar parámetros: primero los pares (id, order) para el CASE
        params = [item for pair in order_data for item in (pair[1], pair[0])]
        params.extend([apiary_id, tuple(new_order)])

        QuestionModel._execute_update(db, query, params)
