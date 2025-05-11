from flask import current_app
from flask_restx import Namespace, Resource, fields
from app.services.email_service import send_newsletter_email, style_newsletter_message
from .models import newsletter_input_model, newsletter_send_report_model, success_response_model, error_response_model
from app.extensions import limiter

ns = Namespace('Newsletter', description='Opérations relatives à l\'envoi de newsletters')

# Modèles
newsletter_input = ns.model('NewsletterInput', newsletter_input_model)
newsletter_report = ns.model('NewsletterSendReport', newsletter_send_report_model)
# success_response et error_response sont déjà définis dans models.py, mais on peut les réimporter pour la clarté
# ou les utiliser via l'objet 'api' de Flask-RESTx si partagés globalement.

@ns.route('/send')
class NewsletterSendResource(Resource):
    # @ns.doc(security='apikey') # Décommentez si vous avez une authentification API
    @ns.expect(newsletter_input)
    @ns.response(200, 'Rapport d\'envoi de la newsletter', newsletter_report)
    @ns.response(400, 'Données d\'entrée invalides', ns.model('ErrorResponse', error_response_model))
    @ns.response(500, 'Erreur interne du serveur', ns.model('ErrorResponse', error_response_model))
    @limiter.limit("10 per hour") # Limite plus stricte pour l'envoi en masse
    def post(self):
        """
        Envoie une newsletter à une liste d'abonnés.
        Le message peut être en Markdown ou HTML. Il sera stylisé.
        """
        data = ns.payload
        subject = data.get('subject')
        message_content = data.get('message_content')
        subscribers = data.get('subscribers', [])
        custom_template_vars = data.get('custom_template_vars', {})

        if not subscribers:
            return {'status': 'error', 'message': 'Aucun abonné fourni.'}, 400

        # Ajout de variables par défaut pour le template
        default_vars = {
            'company_name': 'Votre Super Entreprise',
            'current_year': '2024', # Mieux: datetime.date.today().year
            'unsubscribe_link': 'https://example.com/unsubscribe' # Doit être dynamique
        }
        template_vars = {**default_vars, **custom_template_vars, 'subject': subject}


        try:
            # Préparer et styliser le contenu de l'email une seule fois
            styled_html_content = style_newsletter_message(message_content, template_vars)
        except Exception as e:
            current_app.logger.error(f"Erreur de stylisation du message de newsletter: {e}")
            return {'status': 'error', 'message': f'Erreur de stylisation du message: {e}'}, 500
        
        sent_count = 0
        failed_emails = []

        # Pour un grand nombre d'abonnés, ceci devrait être une tâche en arrière-plan (ex: Celery)
        for email_addr in subscribers:
            # TODO: Valider chaque email_addr ici (format)
            if send_newsletter_email(subject, styled_html_content, email_addr):
                sent_count += 1
            else:
                failed_emails.append(email_addr)
        
        current_app.logger.info(f"Rapport d'envoi newsletter: {sent_count} envoyés, {len(failed_emails)} échecs.")
        
        report = {
            'total_sent': sent_count,
            'total_failed': len(failed_emails),
            'errors': failed_emails
        }
        return report, 200