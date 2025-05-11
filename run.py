from app import create_app
from dotenv import load_dotenv

load_dotenv() # S'assurer que .env est chargé avant create_app si config est lue tôt

application = create_app() # Vercel cherche une variable `application` ou `app`

if __name__ == '__main__':
    # Utiliser les configurations de host et port de Flask si définies, sinon valeurs par défaut
    # host = application.config.get('HOST', '127.0.0.1')
    # port = application.config.get('PORT', 5000)
    # debug = application.config.get('DEBUG', False)
    # application.run(host=host, port=port, debug=debug)
    application.run(debug=application.config.get('DEBUG', True)) # Simplifié pour dev local