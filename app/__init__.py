from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import os

from config import get_config
from .extensions import mail, limiter
from .apis import api_bp # Blueprint principal de l'API
from .utils.error_handlers import handle_werkzeug_exception, handle_generic_exception

def create_app():
    app = Flask(__name__)
    config_obj = get_config()
    app.config.from_object(config_obj)

    # Créer le dossier d'upload s'il n'existe pas
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialiser les extensions
    mail.init_app(app)
    
    if app.config['RATELIMIT_ENABLED']:
        limiter.init_app(app)

    if app.config.get('CORS_ORIGINS'):
        CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}}, supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'])

    # Enregistrer le Blueprint de l'API
    app.register_blueprint(api_bp, url_prefix='/api')

    # Enregistrement global des gestionnaires d'erreurs
    app.register_error_handler(HTTPException, handle_werkzeug_exception)
    app.register_error_handler(Exception, handle_generic_exception)


    @app.route('/')
    def health_check():
        return "API is healthy and running!"

    return app