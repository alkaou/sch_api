# Fichier de configuration centralisé

class AppConfig:
    # Configuration par défaut pour le modèle Gemini
    GEMINI_DEFAULT_MODEL = 'gemini-2.5-pro'
    GEMINI_DEFAULT_TEMPERATURE = 0.8
    GEMINI_DEFAULT_MAX_TOKENS = 4096

# Instance unique de la configuration pour l'application.
# Dans une application réelle, cela pourrait être une classe plus complexe
# qui lit/écrit depuis un fichier ou une base de données.
config = AppConfig()
