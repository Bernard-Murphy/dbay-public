from flask import Blueprint, request, jsonify
from .services import notification_service

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/send', methods=['POST'])
def send_notification():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    notification_service.send_notification(user_id, message, 'manual')
    return jsonify({'status': 'sent'})
