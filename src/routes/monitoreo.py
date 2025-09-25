from flask import Blueprint, request, jsonify, g
from datetime import datetime 
from src.controllers.monitoreo import MonitoreoController
from src.database.db import get_db
from src.middleware.jwt import jwt_required

def create_monitoreo_routes():
    monitoreo_bp = Blueprint('monitoreo_routes', __name__)

    @monitoreo_bp.route('/monitoreos', methods=['POST'])
    def create_monitoreo():
        db = get_db()
        controller = MonitoreoController(db)

        data = request.get_json()
        required = ['id_colmena', 'id_apiario', 'respuestas']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            monitoreo_id = controller.create_monitoreo(
                data['id_colmena'],
                data['id_apiario'],
                data.get('fecha'),
                data['respuestas'],
                data.get('datos_adicionales')
            )
            return jsonify({
                'id': monitoreo_id,
                'message': 'Monitoreo creado exitosamente'
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @monitoreo_bp.route('/monitoreos', methods=['GET'])
    def get_all_monitoreos():
        db = get_db()
        controller = MonitoreoController(db)
        
        try:
            monitoreos = controller.get_all_monitoreos()
            return jsonify(monitoreos), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @monitoreo_bp.route('/monitoreos/<int:monitoreo_id>', methods=['GET'])
    def get_monitoreo(monitoreo_id):
        db = get_db()
        controller = MonitoreoController(db)
        
        try:
            monitoreo = controller.get_monitoreo(monitoreo_id)
            if not monitoreo:
                return jsonify({'error': 'Monitoreo not found'}), 404
            return jsonify(monitoreo), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @monitoreo_bp.route('/apiarios/<int:apiario_id>/monitoreos', methods=['GET'])
    def get_monitoreos_by_apiario(apiario_id):
        db = get_db()
        controller = MonitoreoController(db)
        
        try:
            monitoreos = controller.get_monitoreos_by_apiario(apiario_id)
            return jsonify(monitoreos), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @monitoreo_bp.route('/colmenas/<int:colmena_id>/monitoreos', methods=['GET'])
    def get_monitoreos_by_colmena(colmena_id):
        db = get_db()
        controller = MonitoreoController(db)
        
        try:
            monitoreos = controller.get_monitoreos_by_colmena(colmena_id)
            return jsonify(monitoreos), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @monitoreo_bp.route('/monitoreo/iniciar', methods=['POST'])
    def iniciar_monitoreo_voz():
        """Endpoint para iniciar monitoreo por voz"""
        try:
            return jsonify({
                'status': 'success',
                'message': 'Monitoreo por voz iniciado',
                'maya_active': True
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @monitoreo_bp.route('/health', methods=['GET'])
    def health_check():
        """Endpoint para verificar el estado del servidor"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'beehive-monitoring-api'
        }), 200

    @monitoreo_bp.route('/stats', methods=['GET'])
    @jwt_required
    def get_stats():
        """Endpoint para obtener estadísticas del sistema"""
        db = get_db()
        controller = MonitoreoController(db)
        user_id = g.current_user_id
        
        try:
            stats = controller.get_system_stats(user_id)
            return jsonify(stats), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return monitoreo_bp
