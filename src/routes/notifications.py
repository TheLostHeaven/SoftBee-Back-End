from flask import Blueprint, request, jsonify
import requests
import os
from datetime import datetime, timedelta
from src.database.db import get_db
import sqlite3

notifications_bp = Blueprint('notification_routes', __name__)

FCM_URL = 'https://fcm.googleapis.com/fcm/send'
FCM_KEY = os.getenv('FCM_SERVER_KEY')

@notifications_bp.route('/queen_replacements', methods=['POST'])
def schedule_queen_replacement():
    data = request.get_json()
    db = get_db()
    
    required_fields = ['colmena', 'fecha', 'device_token', 'notificaciones']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO queen_replacements 
            (colmena, fecha, device_token) 
            VALUES (?, ?, ?)
        """, (data['colmena'], data['fecha'], data['device_token']))
        db.commit()
        replacement_id = cursor.lastrowid
        
        replacement_date = datetime.fromisoformat(data['fecha'])
        
        if data['notificaciones'].get('dia_antes', False):
            notify_date = replacement_date - timedelta(days=1)
            _schedule_notification(
                data['device_token'],
                "Recordatorio: Reemplazo de reina",
                f"Mañana se realizará el reemplazo en {data['colmena']}",
                notify_date
            )
        
        if data['notificaciones'].get('dia_evento', False):
            _schedule_notification(
                data['device_token'],
                "Hoy: Reemplazo de reina",
                f"Hoy es el día del reemplazo en {data['colmena']}",
                replacement_date
            )
        
        return jsonify({'status': 'success', 'id': replacement_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _schedule_notification(token, title, body, schedule_time):
    if schedule_time < datetime.now():
        return

    headers = {
        'Authorization': f'key={FCM_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'to': token,
        'notification': {
            'title': title,
            'body': body,
            'sound': 'default'
        },
        'data': {
            'type': 'queen_replacement',
            'click_action': 'FLUTTER_NOTIFICATION_CLICK'
        },
        'android': {
            'priority': 'high'
        },
        'apns': {
            'headers': {
                'apns-priority': '10'
            }
        }
    }
    
    try:
        response = requests.post(FCM_URL, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"Error al enviar notificación: {response.text}")
    except Exception as e:
        print(f"Error al programar notificación: {str(e)}")