from flask import Blueprint, request, jsonify
from .services import messaging_service

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/threads', methods=['POST'])
def create_thread():
    data = request.json
    participants = data.get('participants')
    listing_id = data.get('listing_id')
    order_id = data.get('order_id')
    
    if not participants or len(participants) < 2:
        return jsonify({"error": "Participants required"}), 400
        
    thread_id = messaging_service.create_thread(participants, listing_id, order_id)
    return jsonify({"thread_id": thread_id}), 201

@messaging_bp.route('/threads/<thread_id>/messages', methods=['POST'])
def send_message(thread_id):
    data = request.json
    sender_id = request.headers.get('X-User-ID') or 'test-user'
    body = data.get('body')
    
    if not body:
        return jsonify({"error": "Body required"}), 400
        
    message = messaging_service.send_message(thread_id, sender_id, body)
    return jsonify(message), 201

@messaging_bp.route('/threads', methods=['GET'])
def get_threads():
    user_id = request.headers.get('X-User-ID') or 'test-user'
    threads = messaging_service.get_threads(user_id)
    return jsonify(threads)

@messaging_bp.route('/threads/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    thread = messaging_service.get_messages(thread_id)
    if not thread:
        return jsonify({"error": "Thread not found"}), 404
    return jsonify(thread)
