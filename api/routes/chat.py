from flask import Blueprint, request, jsonify
from ..services.gemini_service import gemini_service
from ..services.file_processor import file_processor
import PIL.Image
import io

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def handle_chat():
    """Endpoint pour interagir avec le chatbot Gemini, avec support de fichiers."""
    if 'message' not in request.form:
        return jsonify({"error": "Le champ 'message' est manquant."}), 400

    message = request.form['message']
    user_id = request.form.get("user_id", "default_user")
    # La configuration pourrait être passée en JSON dans un champ de formulaire
    config = {}

    file_part = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            # Pour Gemini, nous devons passer l'image sous forme d'objet PIL
            # ou le contenu textuel pour les autres fichiers.
            if 'image' in file.mimetype:
                try:
                    img = PIL.Image.open(file.stream)
                    file_part = img
                except Exception as e:
                    return jsonify({"error": f"Impossible de lire le fichier image: {e}"}), 400
            else:
                # Pour les PDF/DOCX, on extrait le texte et on l'ajoute au message
                text_content = file_processor.extract_text(file, file.mimetype)
                if 'text' in text_content:
                    message += "\n\n--- Contenu du fichier joint ---\n" + text_content['text']

    response = gemini_service.generate_chat_response(message, file_part, config)

    if "error" in response:
        return jsonify(response), 500

    # print(jsonify(response))
    return jsonify(response), 200

