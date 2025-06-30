from flask import Blueprint, request, jsonify, current_app
from ..controllers.questions import QuestionController
from src.database.db import get_db
import json
import os

def create_question_routes():
    question_bp = Blueprint('question_routes', __name__)

    @question_bp.route('/questions/load_defaults/<int:apiary_id>', methods=['POST'])
    def load_default_questions(apiary_id):
        """Carga preguntas predeterminadas desde un archivo JSON"""
        db = get_db()
        controller = QuestionController(db)
        
        # Ruta al archivo de configuración
        config_path = os.path.join(current_app.root_path, 'config', 'preguntas_config.json')
        if not os.path.exists(config_path):
            return jsonify({'error': 'Archivo de configuración no encontrado'}), 404

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            preguntas_cargadas = []
            for i, pregunta in enumerate(config['preguntas']):
                # Mapeo de tipos: en el JSON viene 'opcion', en la BD es 'opciones'
                tipo_pregunta = pregunta['tipo']

                # Crear la pregunta
                question_id = controller.create_question(
                    apiary_id=apiary_id,
                    external_id=pregunta['id'],
                    question_text=pregunta['pregunta'],
                    question_type=pregunta['tipo'],
                    is_required=pregunta['obligatoria'],
                    display_order=i + 1,
                    min_value=pregunta.get('min'),
                    max_value=pregunta.get('max'),
                    options=pregunta.get('opciones'),
                    depends_on=None,  # No hay dependencias en el JSON
                    is_active=True
                )
                preguntas_cargadas.append(question_id)
            
            return jsonify({
                'message': f'Se cargaron {len(preguntas_cargadas)} preguntas por defecto',
                'question_ids': preguntas_cargadas
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @question_bp.route('/questions', methods=['POST'])
    def create_question():
        """Crea una nueva pregunta personalizada"""
        db = get_db()
        controller = QuestionController(db)
        data = request.get_json()

        required_fields = ['apiary_id', 'question_text', 'question_type']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        try:
            question_id = controller.create_question(
                apiary_id=data['apiary_id'],
                question_text=data['question_text'],
                question_type=data['question_type'],
                is_required=data.get('is_required', False),
                display_order=data.get('display_order', 0),
                min_value=data.get('min_value'),
                max_value=data.get('max_value'),
                options=data.get('options'),
                depends_on=data.get('depends_on'),
                is_active=data.get('is_active', True),
                external_id=data.get('external_id')
            )
            return jsonify({'id': question_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @question_bp.route('/questions/<int:question_id>', methods=['GET'])
    def get_question(question_id):
        """Obtiene una pregunta por su ID"""
        db = get_db()
        controller = QuestionController(db)
        question = controller.get_question(question_id)
        if question:
            return jsonify(question), 200
        return jsonify({'error': 'Pregunta no encontrada'}), 404

    @question_bp.route('/apiaries/<int:apiary_id>/questions', methods=['GET'])
    def get_apiary_questions(apiary_id):
        """Obtiene todas las preguntas de un apiario"""
        db = get_db()
        controller = QuestionController(db)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        questions = controller.get_apiary_questions(apiary_id, active_only)
        return jsonify(questions), 200

    @question_bp.route('/questions/<int:question_id>', methods=['PUT'])
    def update_question(question_id):
        """Actualiza una pregunta existente"""
        db = get_db()
        controller = QuestionController(db)
        data = request.get_json()
        try:
            controller.update_question(question_id, **data)
            return jsonify({'message': 'Pregunta actualizada'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @question_bp.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """Elimina una pregunta"""
        db = get_db()
        controller = QuestionController(db)
        try:
            controller.delete_question(question_id)
            return jsonify({'message': 'Pregunta eliminada'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @question_bp.route('/apiaries/<int:apiary_id>/questions/reorder', methods=['PUT'])
    def reorder_questions(apiary_id):
        """Reordena las preguntas de un apiario"""
        db = get_db()
        controller = QuestionController(db)
        data = request.get_json()
        if 'order' not in data or not isinstance(data['order'], list):
            return jsonify({'error': 'Se requiere una lista de IDs en "order"'}), 400
        try:
            controller.reorder_questions(apiary_id, data['order'])
            return jsonify({'message': 'Orden de preguntas actualizado'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    return question_bp