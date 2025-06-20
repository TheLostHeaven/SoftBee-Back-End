from flask import Blueprint, request, jsonify
from ..controllers.questions import QuestionController
from src.database.db import get_db

def create_question_routes():
    question_bp = Blueprint('question_routes', __name__)

    @question_bp.route('/questions', methods=['POST'])
    def create_question():
        db = get_db()
        controller = QuestionController(db)

        data = request.get_json()
        required = ['apiary_id', 'question_id', 'question_text', 'question_type']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            question_id = controller.create_question(
                data['apiary_id'],
                data['question_id'],
                data['question_text'],
                data['question_type'],
                data.get('is_required', False),
                data.get('display_order', 0),
                data.get('min_value'),
                data.get('max_value'),
                data.get('options'),
                data.get('depends_on'),
                data.get('is_active', True)
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
