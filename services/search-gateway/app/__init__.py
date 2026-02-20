from flask import Flask
from .routes import search_bp

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def health():
        return {'status': 'ok'}
        
    app.register_blueprint(search_bp, url_prefix='/api/v1')
    
    return app
