from flask import jsonify
from werkzeug.exceptions import HTTPException

def handle_werkzeug_exception(e: HTTPException):
    """Gère les exceptions HTTP de Werkzeug (ex: 404, 400)."""
    response = e.get_response()
    response.data = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }).data
    response.content_type = "application/json"
    return response

def handle_generic_exception(e: Exception):
    """Gère toutes les autres exceptions non interceptées."""
    # Loggez l'erreur ici pour le débogage en production
    # current_app.logger.error(f"Unhandled exception: {e}", exc_info=True)
    
    # Ne pas exposer les détails de l'erreur interne en production
    from flask import current_app
    if current_app.config['DEBUG']:
        error_message = str(e)
    else:
        error_message = "An unexpected error occurred on the server."

    response = jsonify({
        "code": 500,
        "name": "Internal Server Error",
        "description": error_message
    })
    response.status_code = 500
    return response