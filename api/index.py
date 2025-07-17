import os
from flask import Flask, jsonify
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Enregistrer les blueprints
    from .routes.chat import chat_bp
    from .routes.config import config_bp
    app.register_blueprint(chat_bp, url_prefix='/')
    app.register_blueprint(config_bp, url_prefix='/')

    @app.route('/')
    def home():
        return 'API School Manager is running!'

    @app.route('/health')
    def health_check():
        """Vérifie le statut de l'API et des services externes."""
        # Test simple de la clé API Gemini
        gemini_status = "healthy" if os.getenv("GOOGLE_API_KEY") else "misconfigured"
        
        return jsonify({
            "status": "ok",
            "services": {
                "flask": "healthy",
                "gemini": gemini_status,
                "storage": "not_implemented" # Sera mis à jour plus tard
            }
        }), 200

    return app

# Instance de l'application pour Vercel
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

