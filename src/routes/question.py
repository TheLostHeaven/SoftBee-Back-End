# from flask import Blueprint, request, jsonify, current_app, g
# from src.controllers.questions import QuestionController
# from src.database.db import get_db

# question_bp = Blueprint('questions', __name__)

# @question_bp.route('/questions', methods=['GET'])
# def get_questions():
#     db = get_db()
#     try:
#         questions = QuestionController.get_all_questions(db)
#         return jsonify(questions)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         db.close()

# # GET /questions/<id> - Obtener una pregunta específica
# @question_bp.route('/questions/<int:question_id>', methods=['GET'])
# def get_question(question_id):
#     db = get_db()
#     try:
#         question = QuestionController.get_question_by_id(db, question_id)
#         if not question:
#             return jsonify({'error': 'Pregunta no encontrada'}), 404
#         return jsonify(question)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         db.close()

# # POST /questions - Crear una nueva pregunta
# @question_bp.route('/questions', methods=['POST'])
# def create_question():
#     db = get_db()
#     try:
#         data = request.get_json()
#         question_id = QuestionController.create_question(db, data)
#         return jsonify({'id': question_id}), 201
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         db.close()

# # PUT /questions/<id> - Actualizar una pregunta
# @question_bp.route('/questions/<int:question_id>', methods=['PUT'])
# def update_question(question_id):
#     db = get_db()
#     try:
#         data = request.get_json()
#         QuestionController.update_question(db, question_id, data)
#         return jsonify({'message': 'Pregunta actualizada correctamente'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         db.close()

# # DELETE /questions/<id> - Eliminar una pregunta
# @question_bp.route('/questions/<int:question_id>', methods=['DELETE'])
# def delete_question(question_id):
#     db = get_db()
#     try:
#         QuestionController.delete_question(db, question_id)
#         return jsonify({'message': 'Pregunta eliminada correctamente'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 404
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         db.close()

# # GET /questions/type/<tipo> - Obtener preguntas por tipo
# @question_bp.route('/questions/type/<string:tipo>', methods=['GET'])
# def get_questions_by_type(tipo):
#     db = get_db()
#     try:
#         questions = QuestionController.get_questions_by_type(db, tipo)
#         return jsonify(questions)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         db.close()