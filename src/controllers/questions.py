from src.models.questions import QuestionModel

class QuestionController:
    @staticmethod
    def get_all_questions(db):
        """Obtiene todas las preguntas formateadas"""
        raw_questions = QuestionModel.get_all_raw(db)
        return [QuestionController._format_question(q) for q in raw_questions]

    @staticmethod
    def get_question_by_id(db, question_id):
        """Obtiene una pregunta formateada por ID"""
        raw_question = QuestionModel.get_by_id_raw(db, question_id)
        return QuestionController._format_question(raw_question) if raw_question else None

    @staticmethod
    def create_question(db, question_data):
        """Crea una nueva pregunta con validación"""
        # Validación básica
        required_fields = ['pregunta', 'tipo', 'obligatorio']
        if not all(field in question_data for field in required_fields):
            raise ValueError("Faltan campos requeridos")

        # Lógica específica para tipos de pregunta
        if question_data['tipo'] == 'opcion_multiple' and 'opciones' not in question_data:
            raise ValueError("Las preguntas de opción múltiple requieren opciones")

        # Crear la pregunta
        question_id = QuestionModel.create_raw(
            db,
            pregunta=question_data['pregunta'],
            tipo=question_data['tipo'],
            obligatorio=question_data['obligatorio'],
            min_val=question_data.get('min_val'),
            max_val=question_data.get('max_val'),
            opciones=question_data.get('opciones')
        )
        
        return question_id

    @staticmethod
    def update_question(db, question_id, update_data):
        """Actualiza una pregunta con validación"""
        # Validar que la pregunta existe
        if not QuestionModel.get_by_id_raw(db, question_id):
            raise ValueError("Pregunta no encontrada")

        # Actualizar
        success = QuestionModel.update_raw(db, question_id, **update_data)
        if not success:
            raise ValueError("No se proporcionaron campos válidos para actualizar")
        return True

    @staticmethod
    def delete_question(db, question_id):
        """Elimina una pregunta con validación"""
        # Validar que la pregunta existe
        if not QuestionModel.get_by_id_raw(db, question_id):
            raise ValueError("Pregunta no encontrada")
            
        return QuestionModel.delete_raw(db, question_id)

    @staticmethod
    def get_questions_by_type(db, tipo):
        """Obtiene preguntas formateadas por tipo"""
        raw_questions = QuestionModel.get_by_type_raw(db, tipo)
        return [QuestionController._format_question(q) for q in raw_questions]

    @staticmethod
    def _format_question(raw_question):
        """Formatea los datos de la pregunta para la respuesta"""
        return {
            'id': raw_question['id'],
            'pregunta': raw_question['pregunta'],
            'tipo': raw_question['tipo'],
            'min_val': raw_question['min'],
            'max_val': raw_question['max'],
            'obligatorio': bool(raw_question['obligatorio']),
            'opciones': raw_question['opciones'].split(',') if raw_question['opciones'] else None,
            'id_externo': raw_question['id_externo']
        }