import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("La clé API Google (GOOGLE_API_KEY) n'est pas définie.")
        genai.configure(api_key=self.api_key)

    def generate_chat_response(self, message: str, file_part: dict, config: dict) -> dict:
        """Génère une réponse de chat en utilisant le modèle Gemini, potentiellement avec un fichier."""
        from ..config import config as app_config

        try:
            # Utiliser la configuration de la requête si fournie, sinon la configuration globale
            model_params = {
                "temperature": config.get("temperature", app_config.GEMINI_DEFAULT_TEMPERATURE),
                # On pourrait ajouter d'autres paramètres ici
            }
            
            model = genai.GenerativeModel(
                app_config.GEMINI_DEFAULT_MODEL,
                generation_config=model_params
            )
            
            # Construire le contenu de la requête (texte + image si présente)
            content_parts = [message]
            if file_part:
                content_parts.append(file_part)

            response = model.generate_content(content_parts)
            
            # Le calcul de l'usage est fourni par l'API
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
                "cost": "not_calculated"
            }

            return {
                "reply": response.text,
                "usage": usage
            }
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API Gemini: {e}")
            return {"error": "Impossible de communiquer avec le service Gemini."}

gemini_service = GeminiService()
