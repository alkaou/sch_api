from flask import Blueprint, request, jsonify
from ..config import config

config_bp = Blueprint('config', __name__)

@config_bp.route('/config', methods=['POST'])
def update_config():
    """Met à jour la configuration globale de l'application."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Données de configuration manquantes."}), 400

    # Mettre à jour les attributs de l'objet config
    for key, value in data.items():
        if hasattr(config, key.upper()):
            setattr(config, key.upper(), value)
    
    return jsonify({"message": "Configuration mise à jour avec succès."}), 200

@config_bp.route('/config', methods=['GET'])
def get_config():
    """Récupère la configuration actuelle."""
    current_config = {key: getattr(config, key) for key in dir(config) if not key.startswith('__')}
    return jsonify(current_config)
