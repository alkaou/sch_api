import requests
import json
from flask import current_app
# Pour Gemini, vous pouvez utiliser la bibliothèque google-generativeai si vous préférez
# import google.generativeai as genai

# Configuration de la SDK Gemini (si utilisée)
# genai.configure(api_key=current_app.config['GEMINI_API_KEY'])

class AIService:
    def __init__(self):
        self.openai_api_key = current_app.config['OPENAI_API_KEY']
        self.gemini_api_key = current_app.config['GEMINI_API_KEY'] # Pour appels HTTP directs
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"
        # L'endpoint Gemini varie si vous utilisez v1beta ou v1
        # Exemple pour v1beta (modèles génériques)
        self.gemini_endpoint_template = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        # Pour les nouveaux modèles Gemini 1.5 Pro, l'API peut être via AI Studio ou Vertex AI, adaptez l'endpoint.

    def _prepare_openai_payload(self, prompt, conversation_history, files_data, params):
        messages = []
        if conversation_history:
            messages.extend(conversation_history) # Doit être au format OpenAI: [{"role": "user/assistant", "content": "..."}]

        # Gestion basique du contenu multimodal pour OpenAI
        content_parts = [{"type": "text", "text": prompt}]
        if files_data:
            for file_info in files_data: # file_info = {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                if file_info.get("type") == "image_url": # OpenAI GPT-4V
                    content_parts.append(file_info)
                # Ajoutez ici la gestion d'autres types de fichiers si OpenAI les supporte directement
                # ou si vous avez un système RAG pour extraire le texte et l'ajouter au prompt.

        messages.append({"role": "user", "content": content_parts})
        
        payload = {
            "model": params.get("model_id", "gpt-4-turbo-preview"), # ou gpt-4o, gpt-4 etc.
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "max_tokens": params.get("max_tokens", 1024),
            # Ajoutez d'autres paramètres OpenAI supportés (top_p, frequency_penalty, etc.)
        }
        # "reasoning", "tool_choice" etc. sont des concepts plus avancés (function calling/tools)
        # qui nécessitent une structuration spécifique du payload et des fonctions définies.
        # Pour un "paramètre de raisonnement", cela pourrait influencer le prompt système ou les outils disponibles.
        return payload

    def _prepare_gemini_payload(self, prompt, conversation_history, files_data, params):
        # Gemini API (REST) attend un format "contents"
        # https://ai.google.dev/docs/gemini_api_overview?hl=fr#chat
        contents = []
        if conversation_history: # Doit être au format Gemini: [{"role": "user/model", "parts": [{"text": "..."}]}]
            contents.extend(conversation_history)

        current_parts = [{"text": prompt}]
        if files_data:
            for file_info in files_data: # file_info = {"mime_type": "image/jpeg", "data": "base64_encoded_string"}
                current_parts.append({"inline_data": file_info})
        
        contents.append({"role": "user", "parts": current_parts})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": params.get("temperature", 0.7),
                "maxOutputTokens": params.get("max_tokens", 1024),
                "topP": params.get("top_p", 1.0),
                "topK": params.get("top_k", 40)
                # Ajoutez d'autres paramètres de generationConfig
            },
            "safetySettings": params.get("safety_settings", [ # Exemple
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
            ])
        }
        # Le "changement de modèle IA" se fait en ciblant le bon endpoint Gemini ou en spécifiant le modèle.
        # Le "raisonnement" pour Gemini pourrait être activé via des prompts spécifiques ou des tools (si supportés par le modèle visé).
        return payload

    def call_openai(self, prompt, conversation_history=None, files_data=None, params=None):
        if not self.openai_api_key:
            return None, "OpenAI API Key non configurée."
        if params is None: params = {}

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        payload = self._prepare_openai_payload(prompt, conversation_history, files_data, params)
        
        current_app.logger.debug(f"OpenAI Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(self.openai_endpoint, headers=headers, json=payload, timeout=120) # Timeout augmenté
            response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP
            return response.json(), None
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erreur API OpenAI: {e} - Response: {e.response.text if e.response else 'N/A'}")
            error_detail = e.response.json() if e.response and e.response.headers.get('Content-Type') == 'application/json' else str(e)
            return None, f"Erreur de communication avec l'API OpenAI: {error_detail}"

    def call_gemini(self, prompt, conversation_history=None, files_data=None, params=None):
        if not self.gemini_api_key:
            return None, "Gemini API Key non configurée."
        if params is None: params = {}

        model_id = params.get("model_id", "gemini-1.5-flash-latest") # ou gemini-1.5-pro-latest, gemini-pro, etc.
        # Assurez-vous que le model_id est compatible avec l'endpoint que vous utilisez.
        # Les modèles "flash" et "pro" (non -vision) sont text-only. "gemini-pro-vision" gère les images.
        # Les nouveaux modèles comme Gemini 1.5 Pro via AI Studio API utilisent un endpoint différent.
        # Exemple d'endpoint pour les modèles d'AI Studio (v1beta)
        endpoint = self.gemini_endpoint_template.format(model=model_id, api_key=self.gemini_api_key)

        payload = self._prepare_gemini_payload(prompt, conversation_history, files_data, params)
        headers = {"Content-Type": "application/json"}

        current_app.logger.debug(f"Gemini Payload: {json.dumps(payload, indent=2)}")
        current_app.logger.debug(f"Gemini Endpoint: {endpoint}")

        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            # Gemini peut renvoyer une réponse vide si le contenu est bloqué par les filtres de sécurité
            # sans lever d'erreur HTTP. Il faut vérifier le `promptFeedback`.
            response_data = response.json()
            if response_data.get("candidates") is None and response_data.get("promptFeedback"):
                block_reason = response_data["promptFeedback"].get("blockReason")
                if block_reason:
                    return None, f"Contenu bloqué par Gemini. Raison: {block_reason}. Détails: {response_data['promptFeedback'].get('safetyRatings')}"
            
            return response_data, None
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erreur API Gemini: {e} - Response: {e.response.text if e.response else 'N/A'}")
            error_detail = e.response.json() if e.response and e.response.headers.get('Content-Type') == 'application/json' else str(e)
            return None, f"Erreur de communication avec l'API Gemini: {error_detail}"