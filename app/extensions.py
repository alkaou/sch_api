from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

mail = Mail()
limiter = Limiter(
    key_func=get_remote_address, # Identifie les clients par leur adresse IP
    # default_limits=["200 per day", "50 per hour"] # Limites par défaut (optionnel)
)