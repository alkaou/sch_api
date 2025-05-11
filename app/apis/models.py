from flask_restx import fields, reqparse
from werkzeug.datastructures import FileStorage

# Modèle générique pour une réponse de succès
success_response_model = {
    'status': fields.String(description='Statut de l\'opération', example='success'),
    'message': fields.String(description='Message de succès', example='Opération réussie.')
}

# Modèle générique pour une réponse d'erreur
error_response_model = {
    'status': fields.String(description='Statut de l\'opération', example='error'),
    'message': fields.String(description='Message d\'erreur', example='Une erreur est survenue.'),
    'details': fields.Raw(description='Détails techniques de l\'erreur (optionnel)', required=False)
}

# --- Modèles pour Contact API ---
contact_input_model = {
    'name': fields.String(required=True, description='Nom de l\'expéditeur', example='John Doe'),
    'email': fields.String(required=True, description='Email de l\'expéditeur', example='john.doe@example.com', pattern=r'[^@]+@[^@]+\.[^@]+'),
    'message': fields.String(required=True, description='Message à envoyer', min_length=10, example='Bonjour, je souhaiterais plus d\'informations...')
}

# --- Modèles pour Newsletter API ---
newsletter_subscriber_model = fields.String(description='Email de l\'abonné', example='subscriber@example.com', pattern=r'[^@]+@[^@]+\.[^@]+')

newsletter_input_model = {
    'subject': fields.String(required=True, description='Sujet de la newsletter', example='Notre dernière newsletter !'),
    'message_content': fields.String(required=True, description='Contenu de la newsletter (Markdown ou HTML)', example='## Titre\nCeci est notre **newsletter**.'),
    'subscribers': fields.List(newsletter_subscriber_model, required=True, description='Liste des emails des abonnés'),
    'custom_template_vars': fields.Raw(description='Variables optionnelles pour le template email (ex: {"company_name": "Mon Entreprise"})', required=False)
}

newsletter_send_report_model = {
    'total_sent': fields.Integer(description='Nombre total d\'emails envoyés avec succès'),
    'total_failed': fields.Integer(description='Nombre total d\'emails en échec'),
    'errors': fields.List(fields.String, description='Liste des emails qui n\'ont pas pu être envoyés')
}


# --- Modèles pour AI Chat API ---
# Modèle pour un message dans l'historique de conversation (OpenAI & Gemini)
# Note: OpenAI utilise "assistant" pour le modèle, Gemini utilise "model"
# On peut standardiser ou gérer la conversion dans le service. Standardisons sur "assistant".
chat_message_model_fields = {
    'role': fields.String(required=True, description='Rôle du message (user, assistant)', enum=['user', 'assistant', 'model']), # 'model' pour compatibilité Gemini
    'content': fields.Raw(required=True, description='Contenu du message (texte ou structure multimodale)')
    # Pour OpenAI multimodal: content: [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {"url": "data:..."}}]
    # Pour Gemini multimodal: parts: [{"text": "..."}, {"inline_data": {"mime_type": "image/jpeg", "data": "..."}}]
}

# Parser pour les uploads de fichiers (utilisé avec @ns.expect)
file_upload_parser = reqparse.RequestParser()
file_upload_parser.add_argument('file', location='files', type=FileStorage, help="Fichier à téléverser (image, pdf, docx, etc.)")
# On peut ajouter plusieurs arguments 'file' si on veut permettre plusieurs uploads
# file_upload_parser.add_argument('files', location='files', type=FileStorage, action='append', help="Liste de fichiers")

# Modèle d'entrée pour le chat AI (commun pour GPT et Gemini)
ai_chat_input_model = {
    'prompt': fields.String(required=True, description='Le prompt ou la question pour l\'IA', example='Explique la relativité générale.'),
    'conversation_history': fields.List(fields.Nested(chat_message_model_fields), description='Historique de la conversation (optionnel)'),
    'params': fields.Raw(description='Paramètres spécifiques au modèle IA (ex: temperature, max_tokens, model_id). '
                                    'Exemple: {"temperature": 0.5, "max_tokens": 500, "model_id": "gpt-4-turbo"}',
                         example={"temperature": 0.7, "max_tokens": 1024, "custom_instructions": "Réponds comme un pirate."}),
    # Les fichiers sont gérés par le parser `file_upload_parser` et non directement dans ce modèle JSON.
    # Le champ 'files_metadata' est optionnel si on veut passer des métadonnées sur les fichiers uploadés,
    # mais le plus simple est de traiter les `request.files` directement.
}

# Modèle de réponse générique pour l'IA
ai_chat_response_model = {
    'model_name': fields.String(description='Nom du modèle IA utilisé'),
    'response': fields.Raw(description='Réponse brute de l\'API IA'),
    'usage': fields.Raw(description='Informations sur l\'utilisation des tokens (si fournies par l\'IA)', required=False),
    'finish_reason': fields.String(description='Raison de la fin de la génération (si fournie)', required=False),
    'processed_request': fields.Raw(description='La requête telle qu\'envoyée à l\'IA (pour débogage)', required=False)
}


# --- Modèles pour PDF Generator API ---
pdf_input_model = {
    'markdown_content': fields.String(required=True, description='Contenu Markdown à convertir en PDF.', example='# Mon Titre\nCeci est un paragraphe.'),
    'custom_css': fields.String(required=False, description='CSS personnalisé à appliquer au PDF (optionnel).', example='body { font-size: 12pt; }')
}
# La réponse sera un fichier, donc pas de modèle de réponse JSON spécifique, mais on peut définir le type de contenu.