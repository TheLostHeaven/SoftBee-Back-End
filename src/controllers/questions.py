# from src.models.questions import QuestionModel

# class QuestionController:
#     @staticmethod
#     def get_all_questions(db):
#         """Obtiene todas las preguntas formateadas"""
#         raw_questions = QuestionModel.get_all_raw(db)
#         return [QuestionController._format_question(q) for q in raw_questions]

#     @staticmethod
#     def get_question_by_id(db, question_id):
#         """Obtiene una pregunta formateada por ID"""
#         raw_question = QuestionModel.get_by_id_raw(db, question_id)
#         return QuestionController._format_question(raw_question) if raw_question else None

#     @staticmethod
#     def create_question(db, question_data):
#         """Crea una nueva pregunta con validación"""
#         # Validación básica
#         required_fields = ['pregunta', 'tipo', 'obligatorio']
#         if not all(field in question_data for field in required_fields):
#             raise ValueError("Faltan campos requeridos")

#         # Lógica específica para tipos de pregunta
#         if question_data['tipo'] == 'opcion_multiple' and 'opciones' not in question_data:
#             raise ValueError("Las preguntas de opción múltiple requieren opciones")

#         # Crear la pregunta
#         question_id = QuestionModel.create_raw(
#             db,
#             pregunta=question_data['pregunta'],
#             tipo=question_data['tipo'],
#             obligatorio=question_data['obligatorio'],
#             min_val=question_data.get('min_val'),
#             max_val=question_data.get('max_val'),
#             opciones=question_data.get('opciones')
#         )
        
#         return question_id

#     @staticmethod
#     def update_question(db, question_id, update_data):
#         """Actualiza una pregunta con validación"""
#         # Validar que la pregunta existe
#         if not QuestionModel.get_by_id_raw(db, question_id):
#             raise ValueError("Pregunta no encontrada")

#         # Actualizar
#         success = QuestionModel.update_raw(db, question_id, **update_data)
#         if not success:
#             raise ValueError("No se proporcionaron campos válidos para actualizar")
#         return True

#     @staticmethod
#     def delete_question(db, question_id):
#         """Elimina una pregunta con validación"""
#         # Validar que la pregunta existe
#         if not QuestionModel.get_by_id_raw(db, question_id):
#             raise ValueError("Pregunta no encontrada")
            
#         return QuestionModel.delete_raw(db, question_id)

#     @staticmethod
#     def get_questions_by_type(db, tipo):
#         """Obtiene preguntas formateadas por tipo"""
#         raw_questions = QuestionModel.get_by_type_raw(db, tipo)
#         return [QuestionController._format_question(q) for q in raw_questions]

#     @staticmethod
#     def _format_question(raw_question):
#         """Formatea los datos de la pregunta para la respuesta"""
#         return {
#             'id': raw_question['id'],
#             'pregunta': raw_question['pregunta'],
#             'tipo': raw_question['tipo'],
#             'min_val': raw_question['min'],
#             'max_val': raw_question['max'],
#             'obligatorio': bool(raw_question['obligatorio']),
#             'opciones': raw_question['opciones'].split(',') if raw_question['opciones'] else None,
#             'id_externo': raw_question['id_externo']
#         }import json
from ..models.questions import QuestionModel

class QuestionController:
    def __init__(self, db):
        self.db = db
        self.model = QuestionModel
        
    def create_question(self, apiary_id, question_text, question_type, 
                        is_required=False, display_order=0, min_value=None, 
                        max_value=None, options=None, depends_on=None, 
                        is_active=True, external_id=None):
        if question_type == 'opciones' and (not options or len(options) < 2):
            raise ValueError("Las preguntas de opción múltiple requieren al menos 2 opciones")

        if question_type == 'numero' and (min_value is None or max_value is None):
            raise ValueError("Las preguntas numéricas requieren valores mínimos y máximos")

        return self.model.create(
            self.db, apiary_id, question_text, question_type,
            is_required, display_order, min_value, max_value, options,
            depends_on, is_active, external_id)

    def get_question(self, question_id):
        return self.model.get_by_id(self.db, question_id)

    def get_apiary_questions(self, apiary_id, active_only=True):
        return self.model.get_by_apiary(self.db, apiary_id, active_only)

    def update_question(self, question_id, **kwargs):
        if 'question_type' in kwargs:
            if kwargs['question_type'] == 'opciones' and ('options' not in kwargs or len(kwargs['options']) < 2):
                raise ValueError("Option questions require at least 2 options")
            if kwargs['question_type'] == 'numero' and ('min_value' not in kwargs or 'max_value' not in kwargs):
                raise ValueError("Number questions require min and max values")
        self.model.update(self.db, question_id, **kwargs)

    def delete_question(self, question_id):
        self.model.delete(self.db, question_id)

    def reorder_questions(self, apiary_id, new_order):
        if len(new_order) != len(set(new_order)):
            raise ValueError("Duplicate question IDs in order list")
        current_questions = {q['id'] for q in self.get_apiary_questions(apiary_id, False)}
        if set(new_order) != current_questions:
            raise ValueError("Order list doesn't match apiary's questions")
        self.model.reorder(self.db, apiary_id, new_order)