from flask import Blueprint, request, jsonify
from .services import search_service

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search_listings():
    try:
        results = search_service.search(request.args)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@search_bp.route('/saved-searches', methods=['POST'])
def save_search():
    data = request.json
    user_id = request.headers.get('X-User-ID') or 'test-user'
    name = data.get('name')
    query = data.get('query') # Full query object or params
    
    if not name or not query:
        return jsonify({"error": "Name and query required"}), 400
        
    search_id = search_service.save_search(user_id, name, query)
    return jsonify({"id": search_id}), 201

@search_bp.route('/saved-searches', methods=['GET'])
def get_saved_searches():
    user_id = request.headers.get('X-User-ID') or 'test-user'
    searches = search_service.get_saved_searches(user_id)
    return jsonify(searches)

@search_bp.route('/saved-searches/<search_id>', methods=['DELETE'])
def delete_saved_search(search_id):
    user_id = request.headers.get('X-User-ID') or 'test-user'
    search_service.delete_saved_search(search_id, user_id)
    return jsonify({"status": "deleted"})
