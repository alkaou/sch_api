# app/apis/__init__.py

from flask import Blueprint
from flask_restx import Api
# Supprimé : from werkzeug.middleware.proxy_fix import ProxyFix

# Importer les namespaces pour les enregistrer
from .contact_api import ns as contact_ns
from .newsletter_api import ns as newsletter_ns
from .ai_chat_api import ns as ai_chat_ns
from .pdf_generator_api import ns as pdf_generator_ns
# Assurez-vous que tous les autres namespaces que vous pourriez ajouter sont importés ici

# Créer un Blueprint pour regrouper toutes les API
# Il est courant de nommer le blueprint 'api_v1' ou similaire si vous prévoyez plusieurs versions
api_bp = Blueprint('api', __name__)

# Configuration de l'API Flask-RESTx
api = Api(
    api_bp,
    version='1.0',
    title='Mon API Avancée',
    description='Une API Flask experte avec de multiples fonctionnalités et une documentation Swagger.',
    doc='/doc/', # URL pour Swagger UI. Mettre à False pour désactiver en prod si nécessaire.
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Entrez 'Bearer <JWT_TOKEN>' pour l'authentification."
        }
    },
    # security='apikey' # Appliquer globalement l'authentification (décommenter si besoin)
    # validate=True # Déplacé de config.py pour être plus proche, ou laisser dans config
    # catch_all_404s=True # Peut être utile
)

# -- Début de la section à supprimer --
# Middleware pour corriger les informations de proxy (utile derrière Vercel, Nginx, etc.)
# Ceci est important pour que Flask-Limiter et d'autres extensions qui dépendent de l'IP client fonctionnent correctement.
# Le nombre de proxies (ici 1) dépend de votre configuration de déploiement.
# Vercel agit comme un proxy.
# if api.app: # Si l'API est déjà attachée à une app (ce qui est le cas ici via le blueprint)
#     api.app.wsgi_app = ProxyFix(api.app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
# else: # Fallback si l'app n'est pas encore initialisée (moins probable avec les blueprints)
#     @api_bp.before_app_first_request
#     def apply_proxy_fix():
#         from flask import current_app
#         current_app.wsgi_app = ProxyFix(current_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
# -- Fin de la section à supprimer --


# Ajouter les namespaces (endpoints) à l'API
api.add_namespace(contact_ns, path='/contact')
api.add_namespace(newsletter_ns, path='/newsletter')
api.add_namespace(ai_chat_ns, path='/ai')
api.add_namespace(pdf_generator_ns, path='/pdf')
# Ajoutez ici d'autres namespaces

# Vous pouvez ajouter ici des gestionnaires d'erreurs personnalisés pour l'objet api RESTx
@api.errorhandler(Exception)
def default_api_error_handler(error):
    """Renvoie les erreurs non gérées par les namespaces spécifiques au format JSON."""
    from flask import current_app
    # Loggez l'erreur ici
    current_app.logger.error(f"API Error: {error}", exc_info=True)
    # Ne pas exposer les détails de l'erreur interne en production par défaut
    message = str(error) if current_app.config.get('DEBUG', False) else 'Une erreur interne est survenue.'
    # Essayez d'obtenir un code d'erreur standard si disponible
    error_code = getattr(error, 'code', 500)
    # S'assurer que le code est un code d'erreur HTTP valide
    if not isinstance(error_code, int) or error_code < 400 or error_code >= 600:
        error_code = 500
    return {'message': message, 'error_type': error.__class__.__name__}, error_code