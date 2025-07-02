from flask import Blueprint, request, jsonify, current_app
from ..controllers.questions import QuestionController
from src.database.db import get_db
from src.models.hive import hiveModel
import json
import os
import traceback

def create_question_routes():
    question_bp = Blueprint('question_routes', __name__)

    @question_bp.route('/questions/load_defaults/<int:apiary_id>', methods=['POST'])
    def load_default_questions(apiary_id):
        """Carga preguntas predeterminadas desde un archivo JSON"""
        db = get_db()
        controller = QuestionController(db)

        config_path = os.path.join(current_app.root_path, 'config', 'preguntas_config.json')
        if not os.path.exists(config_path):
            return jsonify({'error': 'Archivo de configuración no encontrado'}), 404

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            preguntas = config.get("preguntas", [])
            if not isinstance(preguntas, list):
                return jsonify({'error': 'Formato inválido en el archivo JSON'}), 400

            preguntas_cargadas = []
            from src.models.questions import QuestionModel

            for i, pregunta_data in enumerate(preguntas):
                external_id = pregunta_data.get('id')
                if not external_id:
                    continue

                # Moví estas líneas para que estén antes de usarlas
                question_text = pregunta_data.get('pregunta')
                question_type = pregunta_data.get('tipo')
                category = pregunta_data.get('categoria')
                is_required = pregunta_data.get('obligatoria', False)
                display_order = i + 1
                depends_on = pregunta_data.get('depende_de')
                min_value = pregunta_data.get("min")
                max_value = pregunta_data.get("max")
                opciones = pregunta_data.get('opciones')

                # Validación y limpieza de opciones
                if question_type == 'opciones':
                    if not opciones or not isinstance(opciones, list):
                        raise ValueError(f"❌ Opciones inválidas en '{external_id}'")
                    opciones = [str(op) for op in opciones]

                # Validación para tipo número
                if question_type == 'numero':
                    if min_value is None or max_value is None:
                        raise ValueError(f"❌ Pregunta '{external_id}' tipo número necesita min y max")

                question_id = QuestionModel.insert_or_update_default_question(
                    db,
                    apiary_id=apiary_id,
                    external_id=external_id,
                    question_text=question_text,
                    question_type=question_type,
                    category=category,
                    is_required=is_required,
                    display_order=display_order,
                    min_value=min_value,
                    max_value=max_value,
                    options=opciones,
                    depends_on=depends_on,
                    is_active=True
                )
                preguntas_cargadas.append(question_id)

            return jsonify({
                'message': f'Se cargaron {len(preguntas_cargadas)} preguntas por defecto',
                'question_ids': preguntas_cargadas
            }), 200

        except ValueError as ve:
            print("❌ ValueError en carga de preguntas:", ve)
            traceback.print_exc()
            return jsonify({'error': str(ve), 'type': 'ValueError'}), 400
        except Exception as e:
            print("❌ Error inesperado en carga de preguntas:")
            traceback.print_exc()
            return jsonify({'error': str(e), 'type': 'Exception'}), 500

    @question_bp.route('/apiaries/<int:apiary_id>/questions', methods=['POST'])
    def create_question(apiary_id):
        db = get_db()
        controller = QuestionController(db)
        data = request.get_json()

        required_fields = ['question_text', 'question_type']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        try:
            question_id = controller.create_question(
                apiary_id=apiary_id,
                question_text=data['question_text'],
                question_type=data['question_type'],
                category=data.get('category'),
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
        except ValueError as ve:
            return jsonify({'error': str(ve), 'type': 'ValueError'}), 400
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e), 'type': 'Exception'}), 400

    @question_bp.route('/questions/<int:question_id>', methods=['GET'])
    def get_question(question_id):
        db = get_db()
        controller = QuestionController(db)
        question = controller.get_question(question_id)
        if question:
            return jsonify(question), 200
        return jsonify({'error': 'Pregunta no encontrada'}), 404

    @question_bp.route('/apiaries/<int:apiary_id>/questions', methods=['GET'])
    def get_apiary_questions(apiary_id):
        db = get_db()
        controller = QuestionController(db)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        questions = controller.get_apiary_questions(apiary_id, active_only)
        return jsonify(questions), 200

    @question_bp.route('/questions/<int:question_id>', methods=['PUT'])
    def update_question(question_id):
        db = get_db()
        controller = QuestionController(db)
        data = request.get_json()
        try:
            controller.update_question(question_id, **data)
            return jsonify({'message': 'Pregunta actualizada'}), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 400

    @question_bp.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        db = get_db()
        controller = QuestionController(db)
        try:
            controller.delete_question(question_id)
            return jsonify({'message': 'Pregunta eliminada'}), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 400

    @question_bp.route('/apiaries/<int:apiary_id>/questions/reorder', methods=['PUT'])
    def reorder_questions(apiary_id):
        db = get_db()
        controller = QuestionController(db)
        data = request.get_json()
        if 'order' not in data or not isinstance(data['order'], list):
            return jsonify({'error': 'Se requiere una lista de IDs en "order"'}), 400
        
        try:
            # Convertir a enteros si es necesario
            order_ids = [int(id) for id in data['order']]
            controller.reorder_questions(apiary_id, order_ids)
            return jsonify({'message': 'Orden de preguntas actualizado'}), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 400

    @question_bp.route('/questions/bank', methods=['GET'])
    def get_question_bank():
        try:
            config_path = os.path.join(current_app.root_path, 'config', 'preguntas_config.json')
            if not os.path.exists(config_path):
                return jsonify({'error': 'Archivo de configuración del banco de preguntas no encontrado'}), 404

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            return jsonify(config['preguntas']), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    @question_bp.route('/beehives/<int:beehive_id>/questions', methods=['GET'])
    def get_beehive_questions(beehive_id):
        db = get_db()
        beehive = hiveModel.get_by_id(db, beehive_id)
        if not beehive:
            return jsonify({'error': 'Colmena no encontrada'}), 404
        
        apiary_id = beehive['apiary_id']
        controller = QuestionController(db)
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        try:
            questions = controller.get_apiary_questions(apiary_id, active_only)
            return jsonify(questions), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    return question_bp