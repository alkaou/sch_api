# app/__init__.py

from flask import Flask, jsonify, redirect, url_for # Ajout de redirect, url_for
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import logging
# from logging.handlers import RotatingFileHandler # Commenté si non utilisé

from config import get_config
from .extensions import mail, limiter
from .apis import api_bp # Blueprint principal de l'API
from .utils.error_handlers import handle_werkzeug_exception, handle_generic_exception

def setup_logging(app):
    """Configure le logging pour l'application."""
    if not app.debug and not app.testing:
        # En production
        app.logger.setLevel(logging.INFO)
        app.logger.info("Démarrage de l'API en mode Production/Testing.")
        # Ajouter ici des handlers spécifiques (fichier, etc.) si nécessaire
    else:
        # En mode debug
        app.logger.setLevel(logging.DEBUG)
        app.logger.info("Démarrage de l'API en mode Debug.")

def create_app():
    """Factory pour créer et configurer l'application Flask."""
    app = Flask(__name__)
    config_obj = get_config()
    app.config.from_object(config_obj)

    # Appliquer ProxyFix si nécessaire (typiquement en prod)
    if not app.config.get("DEBUG", False):
         app.wsgi_app = ProxyFix(
             app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1
         )

    # Configurer le logging
    setup_logging(app)

    # --- Bloc potentiellement problématique 1 : Dossier Upload ---
    upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
    if not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder)
            app.logger.info(f"Dossier d'upload créé: {upload_folder}")
        except OSError as e:
            # Erreur possible ici si droits insuffisants
            app.logger.error(f"Impossible de créer le dossier d'upload {upload_folder}: {e}")
    # --- Fin Bloc 1 ---

    # --- Bloc potentiellement problématique 2 : Extensions ---
    try:
        mail.init_app(app)
        if app.config.get("RATELIMIT_ENABLED", True):
            limiter.init_app(app)
        cors_origins = app.config.get("CORS_ORIGINS")
        if cors_origins:
            CORS(app,
                 resources={r"/api/*": {"origins": cors_origins}},
                 supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", True),
                 methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    except Exception as e:
        app.logger.error(f"Erreur lors de l'initialisation des extensions: {e}", exc_info=True)
        # Vous pourriez vouloir arrêter l'app ici si une extension est critique
    # --- Fin Bloc 2 ---

    # --- Bloc potentiellement problématique 3 : Blueprint & Handlers ---
    try:
        app.register_blueprint(api_bp, url_prefix="/api")
        app.register_error_handler(HTTPException, handle_werkzeug_exception)
        app.register_error_handler(Exception, handle_generic_exception)
    except Exception as e:
        app.logger.error(f"Erreur lors de l'enregistrement du blueprint ou des handlers: {e}", exc_info=True)
    # --- Fin Bloc 3 ---


    # --- Bloc potentiellement problématique 4 : Routes ---
    try:
        @app.route("/health")
        def health_check():
            return jsonify({"status": "ok", "message": "API is healthy"}), 200

        @app.route("/")
        def home():
            if app.config.get("DEBUG"):
                try:
                    doc_url = url_for("api.doc")
                    return redirect(doc_url)
                except Exception as e:
                    app.logger.warning(f"Impossible de rediriger vers la documentation API: {e}")
                    return "Bienvenue sur Mon API Avancée. Documentation sur /api/doc/", 200
            else:
                return "Welcome to the Advanced API.", 200
    except Exception as e:
        app.logger.error(f"Erreur lors de la définition des routes de base: {e}", exc_info=True)
    # --- Fin Bloc 4 ---

    app.logger.info("Application Flask créée et configurée avec succès.")
    return app