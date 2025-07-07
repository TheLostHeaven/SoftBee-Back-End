from flask import Blueprint, jsonify, g
from src.controllers.reports import ReportsController
from src.database.db import get_db
from src.middleware.jwt import jwt_required
from flask_cors import CORS

def create_reports_routes():
    reports_bp = Blueprint('reports_routes', __name__)
    CORS(reports_bp, resources={r"/reports/monitoring": {"origins": "*"}})

    @reports_bp.route('/reports/monitoring', methods=['GET'])
    @jwt_required
    def get_monitoring_reports():
        db = get_db()
        controller = ReportsController(db)
        user_id = g.current_user_id

        try:
            reports = controller.get_monitoring_reports(user_id)
            return jsonify(reports), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return reports_bp