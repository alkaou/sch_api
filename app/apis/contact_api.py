from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app.services.email_service import send_contact_email
from .models import contact_input_model, success_response_model, error_response_model
from app.extensions import limiter

ns = Namespace('Contact', description='Opérations relatives au formulaire de contact')

# Modèles pour la documentation et la validation
contact_input = ns.model('ContactInput', contact_input_model)
success_response = ns.model('SuccessResponse', success_response_model)
error_response = ns.model('ErrorResponse', error_response_model)


@ns.route('/')
class ContactResource(Resource):
    @ns.doc('send_contact_message')
    @ns.expect(contact_input)
    @ns.response(200, 'Email envoyé avec succès', success_response)
    @ns.response(400, 'Données d\'entrée invalides', error_response)
    @ns.response(500, 'Erreur interne du serveur', error_response)
    @limiter.limit("5 per minute") # Limite de débit spécifique à cet endpoint
    def post(self):
        """Reçoit les données d'un formulaire de contact et envoie un email."""
        data = ns.payload # Données validées par Flask-RESTx grâce à @ns.expect
        name = data.get('name')
        email = data.get('email')
        message_body = data.get('message')

        # Validation supplémentaire si nécessaire (Flask-RESTx gère les types et 'required')
        if not all([name, email, message_body]):
            # Normalement, ns.expect devrait déjà attraper ça si les champs sont 'required'
            return {'status': 'error', 'message': 'Champs manquants: name, email, message sont requis.'}, 400
        
        if len(message_body) < 10:
             return {'status': 'error', 'message': 'Le message doit contenir au moins 10 caractères.'}, 400

        success, status_message = send_contact_email(name, email, message_body)

        if success:
            current_app.logger.info(f"Email de contact envoyé de la part de {name} ({email})")
            return {'status': 'success', 'message': status_message}, 200
        else:
            current_app.logger.error(f"Échec de l'envoi de l'email de contact de {name} ({email}): {status_message}")
            return {'status': 'error', 'message': status_message}, 500