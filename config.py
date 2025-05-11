import os
from dotenv import load_dotenv

load_dotenv() # Charge les variables depuis .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'une-cle-secrete-par-defaut-pour-dev'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')

    # Flask-Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MY_PROJECT_EMAIL = os.environ.get('MY_PROJECT_EMAIL')

    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Flask-Limiter
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() in ('true', '1', 't')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URI', "memory://")
    RATELIMIT_STRATEGY = "fixed-window" # ou "moving-window"
    RATELIMIT_HEADERS_ENABLED = True

    # Flask-CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    CORS_SUPPORTS_CREDENTIALS = True # Si vous utilisez des cookies/auth headers

    # API Documentation (Flask-RESTx)
    RESTX_SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False # Mettre True si vous ne voulez pas exposer Swagger en prod sans auth
    RESTX_ERROR_404_HELP = False

    # File Uploads
    UPLOAD_FOLDER = 'uploads' # Créez ce dossier s'il n'existe pas
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'md'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'
    # Potentiellement d'autres configs spécifiques au dev

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    # RATELIMIT_STORAGE_URL = "redis://localhost:6379/1" # Utilisez Redis en production

# Choix de la configuration en fonction de FLASK_ENV
config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig,
    default=DevelopmentConfig
)

def get_config():
    env = os.getenv('FLASK_ENV', 'default')
    return config_by_name.get(env, DevelopmentConfig)