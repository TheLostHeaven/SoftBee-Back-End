from flask import Blueprint, request, jsonify, current_app, g
from ..controllers.questions import QuestionController
from src.database.db import get_db
import json
import os

def create_question_routes():
    question_bp = Blueprint('question_routes', __name__)

    @question_bp.route('/questions/load_defaults', methods=['POST'])
    def load_default_questions():
        db = get_db()
        controller = QuestionController(db)
        data = request.get_json()

        apiary_id = data.get('apiary_id')
        if not apiary_id:
            return jsonify({'error': 'apiary_id es requerido'}), 400

        config_path = os.path.join(current_app.root_path, 'config', 'preguntas_config.json')
        if not os.path.exists(config_path):
            return jsonify({'error': 'Archivo de configuración de preguntas no encontrado'}), 500

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            preguntas_cargadas = []
            # Cargar preguntas generales
            for i, p in enumerate(config.get('preguntas', [])):
                question_id = controller.create_question(
                    apiary_id=apiary_id,
                    external_id=p.get('id'),
                    question_text=p.get('pregunta'),
                    question_type=p.get('tipo'),
                    is_required=p.get('obligatoria', False),
                    display_order=i + 1, # Asignar un orden inicial
                    min_value=p.get('min'),
                    max_value=p.get('max'),
                    options=p.get('opciones'),
                    depends_on=p.get('depende_de'),
                    is_active=True
                )
                preguntas_cargadas.append(question_id)
            
            # Cargar preguntas de cámara de producción
            for i, p in enumerate(config.get('preguntas_camara_produccion', [])):
                question_id = controller.create_question(
                    apiary_id=apiary_id,
                    external_id=p.get('id'),
                    question_text=p.get('pregunta'),
                    question_type=p.get('tipo'),
                    is_required=p.get('obligatoria', False),
                    display_order=len(config.get('preguntas', [])) + i + 1, # Continuar el orden
                    min_value=p.get('min'),
                    max_value=p.get('max'),
                    options=p.get('opciones'),
                    depends_on=p.get('depende_de'),
                    is_active=True
                )
                preguntas_cargadas.append(question_id)

            return jsonify({'message': f'Se cargaron {len(preguntas_cargadas)} preguntas por defecto.', 'ids': preguntas_cargadas}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @question_bp.route('/questions', methods=['POST'])
    def create_question():
        db = get_db()
        controller = QuestionController(db)

        data = request.get_json()
        required = ['apiary_id', 'question_text', 'question_type']
        if not all(field in data for field in required):
            return jsonify({'error': 'Faltan campos requeridos: apiary_id, question_text, question_type'}), 400

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

    @question_bp.route('/questions/<question_id>', methods=['GET'])
    def get_question(question_id):
        db = get_db()
        controller = QuestionController(db)

        question = controller.get_question(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        return jsonify(question), 200

    @question_bp.route('/apiaries/<int:apiary_id>/questions', methods=['GET'])
    def get_apiary_questions(apiary_id):
        db = get_db()
        controller = QuestionController(db)

        active_only = request.args.get('active_only', 'true').lower() == 'true'
        questions = controller.get_apiary_questions(apiary_id, active_only)
        return jsonify(questions), 200

    @question_bp.route('/questions/<question_id>', methods=['PUT'])
    def update_question(question_id):
        db = get_db()
        controller = QuestionController(db)

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        try:
            controller.update_question(question_id, **data)
            return jsonify({'message': 'Question updated'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @question_bp.route('/questions/<question_id>', methods=['DELETE'])
    def delete_question(question_id):
        db = get_db()
        controller = QuestionController(db)

        try:
            controller.delete_question(question_id)
            return jsonify({'message': 'Question deleted'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @question_bp.route('/apiaries/<int:apiary_id>/questions/reorder', methods=['PUT'])
    def reorder_questions(apiary_id):
        db = get_db()
        controller = QuestionController(db)

        if 'order' not in request.json or not isinstance(request.json['order'], list):
            return jsonify({'error': 'Order list required'}), 400

        try:
            controller.reorder_questions(apiary_id, request.json['order'])
            return jsonify({'message': 'Questions reordered'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    return question_bp
