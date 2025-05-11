from flask import request, current_app, send_file
from flask_restx import Namespace, Resource, fields, reqparse
from werkzeug.utils import secure_filename
import os
import base64

from app.services.ai_service import AIService
from .models import ai_chat_input_model, ai_chat_response_model, error_response_model, file_upload_parser
from app.extensions import limiter

ns = Namespace('AI Chat', description='Interaction avec les modèles d\'IA conversationnels (GPT et Gemini)')

# Modèles
ai_input = ns.model('AIChatInput', ai_chat_input_model)
ai_response = ns.model('AIChatResponse', ai_chat_response_model)
error_resp = ns.model('ErrorResponseAI', error_response_model) # Renommer pour éviter conflit si nécessaire

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def process_uploaded_files(files):
    """
    Traite les fichiers uploadés.
    Pour l'instant, on va se concentrer sur les images en base64 pour les modèles multimodaux.
    Les PDF/DOCX nécessiteraient une extraction de texte (ex: PyMuPDF, python-docx) pour un RAG simple,
    ou d'être passés tels quels si l'API IA supporte le format directement (ce qui est rare hors SDKs spécifiques).
    """
    files_data_for_ai = []
    if not files:
        return files_data_for_ai

    for file_key in files:
        file_storage = files[file_key]
        if file_storage and file_storage.filename and allowed_file(file_storage.filename):
            filename = secure_filename(file_storage.filename)
            # Sauvegarder temporairement ou traiter en mémoire
            # file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            # file_storage.save(file_path)
            # current_app.logger.info(f"Fichier {filename} uploadé et sauvegardé.")

            # Préparer pour les API IA (exemple pour images)
            file_extension = filename.rsplit('.', 1)[1].lower()
            mime_type = None
            if file_extension in ['jpg', 'jpeg']:
                mime_type = 'image/jpeg'
            elif file_extension == 'png':
                mime_type = 'image/png'
            # Ajoutez d'autres types MIME supportés par les modèles IA
            
            if mime_type:
                try:
                    file_bytes = file_storage.read() # Lire le contenu du fichier
                    file_storage.seek(0) # Important si vous réutilisez file_storage
                    base64_encoded_data = base64.b64encode(file_bytes).decode('utf-8')
                    
                    # Format pour OpenAI GPT-4V (Vision)
                    # files_data_for_ai.append({
                    #     "type": "image_url",
                    #     "image_url": {"url": f"data:{mime_type};base64,{base64_encoded_data}"}
                    # })
                    # Format pour Gemini API (REST)
                    files_data_for_ai.append({
                        "mime_type": mime_type,
                        "data": base64_encoded_data # Gemini prend la data base64 directement
                    })
                    current_app.logger.info(f"Fichier {filename} ({mime_type}) préparé pour l'IA.")
                except Exception as e:
                    current_app.logger.error(f"Erreur de traitement du fichier {filename}: {e}")
            else:
                # Pour PDF, DOCX, etc., vous devriez extraire le texte ici pour un RAG simple
                # ou l'intégrer d'une autre manière selon les capacités du modèle IA
                current_app.logger.warning(f"Type de fichier non géré pour l'envoi direct à l'IA : {filename}")
                # Exemple d'extraction de texte (simpliste)
                # if file_extension == 'txt':
                #    text_content = file_storage.read().decode('utf-8')
                #    files_data_for_ai.append({"type": "text_document", "name": filename, "content": text_content})

    return files_data_for_ai


@ns.route('/chat/<string:model_choice>')
@ns.param('model_choice', 'Choix du modèle IA (gpt ou gemini)')
class AIChatResource(Resource):
    # @ns.doc(security='apikey') # Pour authentification
    @ns.expect(file_upload_parser, ai_input) # file_upload_parser pour la doc Swagger des uploads
    @ns.response(200, 'Réponse de l\'IA', ai_response)
    @ns.response(400, 'Requête invalide', error_resp)
    @ns.response(404, 'Modèle IA non trouvé', error_resp)
    @ns.response(500, 'Erreur serveur ou API IA', error_resp)
    @limiter.limit("60 per hour;20 per minute") # Limites combinées
    def post(self, model_choice):
        """
        Communique avec un modèle d'IA (GPT ou Gemini).
        Permet d'envoyer un prompt, un historique de conversation, des fichiers, et des paramètres.
        Les fichiers sont passés en multipart/form-data (clé 'file'). Les autres données en JSON.
        """
        # Flask-RESTx parse le JSON payload dans ns.payload si Content-Type est application/json.
        # Pour multipart/form-data, il faut accéder aux champs de formulaire et aux fichiers différemment.
        # Une astuce est d'envoyer les données JSON sous un champ de formulaire spécifique (ex: 'json_payload')
        # Ou, comme fait ici, on utilise reqparse pour la partie fichier, et on s'attend à ce que le reste soit dans `request.form` ou `request.json`.
        # Si on utilise `file_upload_parser` avec `@ns.expect`, il s'attend à ce que *tous* les arguments soient dans `args`.
        # Une approche plus flexible pour les API mixtes (fichiers + JSON) :
        
        args = file_upload_parser.parse_args() # Récupère les fichiers
        
        # Récupérer le payload JSON. Peut être envoyé comme 'data' dans form-data ou comme JSON brut.
        if 'application/json' in request.content_type:
            json_payload = request.get_json()
        else:
            # Essayer de parser un champ 'json_data' ou 'payload' du formulaire
            json_str = request.form.get('json_data') or request.form.get('payload')
            if json_str:
                try:
                    json_payload = json.loads(json_str)
                except json.JSONDecodeError:
                    return {'status': 'error', 'message': "Payload JSON invalide dans les données du formulaire."}, 400
            else: # Fallback, RESTx pourrait l'avoir parsé dans ns.payload si c'est un multipart bien formé
                json_payload = ns.payload if ns.payload else {}
        
        prompt = json_payload.get('prompt')
        conversation_history = json_payload.get('conversation_history', [])
        params = json_payload.get('params', {})

        if not prompt:
            return {'status': 'error', 'message': 'Le champ "prompt" est requis.'}, 400

        # Traiter les fichiers uploadés (ceux de args['file'] ou request.files)
        # request.files est un MultiDict, file_upload_parser le met dans args
        uploaded_files = request.files # Utiliser request.files directement est souvent plus simple
        files_data_for_ai = process_uploaded_files(uploaded_files)
        
        ai_service = AIService()
        response_data = None
        error_message = None
        model_used_name = ""

        # "Activation et désactivation des paramètres (raisonnement, changement de model IA, etc)"
        # -> Ceci est géré en passant les paramètres souhaités dans `params`.
        #    Ex: `params: {"model_id": "gpt-4", "temperature": 0.2, "enable_reasoning_module": true}`
        #    Le service IA doit ensuite interpréter ces `params`.
        #    `model_id` permet de changer de modèle.

        if model_choice.lower() == 'gpt':
            model_used_name = params.get("model_id", "gpt-4-turbo-preview") # Ou autre modèle par défaut
            response_data, error_message = ai_service.call_openai(prompt, conversation_history, files_data_for_ai, params)
            if response_data:
                # Structurer la réponse pour le client
                return {
                    "model_name": f"OpenAI {model_used_name}",
                    "response": response_data.get("choices", [{}])[0].get("message", {}).get("content"),
                    "usage": response_data.get("usage"),
                    "finish_reason": response_data.get("choices", [{}])[0].get("finish_reason"),
                    "processed_request": current_app.config['DEBUG'] and ai_service._prepare_openai_payload(prompt, conversation_history, files_data_for_ai, params) or "hidden"
                }, 200

        elif model_choice.lower() == 'gemini':
            model_used_name = params.get("model_id", "gemini-1.5-flash-latest") # Ou autre modèle par défaut Gemini
            response_data, error_message = ai_service.call_gemini(prompt, conversation_history, files_data_for_ai, params)
            if response_data:
                # La structure de réponse de Gemini API peut varier. Adaptez en conséquence.
                # Typiquement, le texte est dans response_data['candidates'][0]['content']['parts'][0]['text']
                try:
                    text_response = ""
                    if response_data.get("candidates"):
                        for part in response_data["candidates"][0].get("content", {}).get("parts", []):
                            if "text" in part:
                                text_response += part["text"]
                    
                    return {
                        "model_name": f"Gemini {model_used_name}",
                        "response": text_response,
                        "usage": response_data.get("usageMetadata"), # Gemini utilise 'usageMetadata'
                        "finish_reason": response_data.get("candidates", [{}])[0].get("finishReason"),
                        "processed_request": current_app.config['DEBUG'] and ai_service._prepare_gemini_payload(prompt, conversation_history, files_data_for_ai, params) or "hidden"
                    }, 200
                except (IndexError, KeyError) as e:
                    current_app.logger.error(f"Erreur de parsing de la réponse Gemini: {e} - Data: {response_data}")
                    error_message = f"Format de réponse inattendu de Gemini: {e}"


        else:
            return {'status': 'error', 'message': f"Modèle IA '{model_choice}' non supporté. Choisissez 'gpt' ou 'gemini'."}, 404

        if error_message:
            return {'status': 'error', 'message': error_message, 'model_name': model_used_name}, 500
        
        # Fallback si aucune condition n'est remplie (ne devrait pas arriver)
        return {'status': 'error', 'message': 'Erreur inattendue lors du traitement de la requête IA.'}, 500