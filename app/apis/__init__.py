from flask import Blueprint
from flask_restx import Api
from werkzeug.middleware.proxy_fix import ProxyFix # Pour Vercel/proxies

# Importer les namespaces pour les enregistrer
from .contact_api import ns as contact_ns
from .newsletter_api import ns as newsletter_ns
from .ai_chat_api import ns as ai_chat_ns
from .pdf_generator_api import ns as pdf_generator_ns

# Créer un Blueprint pour regrouper toutes les API
api_bp = Blueprint('api', __name__)

# Configuration de l'API Flask-RESTx
# Le décorateur @api.errorhandler sera utilisé par défaut pour les erreurs dans ces namespaces
# sauf si un gestionnaire plus spécifique est défini localement dans un namespace.
api = Api(
    api_bp,
    version='1.0',
    title='Mon API Avancée',
    description='Une API Flask experte avec de multiples fonctionnalités et une documentation Swagger.',
    doc='/doc/', # URL pour Swagger UI. Mettre à False pour désactiver en prod si nécessaire.
    authorizations={ # Configuration pour l'authentification (exemple avec Bearer Token JWT)
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Entrez 'Bearer <JWT_TOKEN>' pour l'authentification."
        }
    }
    # security='apikey' # Appliquer globalement l'authentification (décommenter si besoin)
)

# Middleware pour corriger les informations de proxy (utile derrière Vercel, Nginx, etc.)
# Ceci est important pour que Flask-Limiter et d'autres extensions qui dépendent de l'IP client fonctionnent correctement.
# Le nombre de proxies (ici 1) dépend de votre configuration de déploiement.
# Vercel agit comme un proxy.
if api.app: # Si l'API est déjà attachée à une app (ce qui est le cas ici via le blueprint)
    api.app.wsgi_app = ProxyFix(api.app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
else: # Fallback si l'app n'est pas encore initialisée (moins probable avec les blueprints)
    @api_bp.before_app_first_request
    def apply_proxy_fix():
        from flask import current_app
        current_app.wsgi_app = ProxyFix(current_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)


# Ajouter les namespaces (endpoints) à l'API
api.add_namespace(contact_ns, path='/contact')
api.add_namespace(newsletter_ns, path='/newsletter')
api.add_namespace(ai_chat_ns, path='/ai')
api.add_namespace(pdf_generator_ns, path='/pdf')

# Vous pouvez ajouter ici des gestionnaires d'erreurs personnalisés pour l'API
@api.errorhandler(Exception) # Gestionnaire d'erreur par défaut pour l'objet api RESTx
def default_api_error_handler(error):
    """Renvoie les erreurs non gérées par les namespaces spécifiques au format JSON."""
    # Loggez l'erreur ici
    # current_app.logger.error(f"API Error: {error}", exc_info=True)
    message = str(error) if api.app.config['DEBUG'] else 'Une erreur interne est survenue.'
    return {'message': message, 'error_type': error.__class__.__name__}, getattr(error, 'code', 500)