from flask_mail import Message
from flask import current_app, render_template
from app.extensions import mail
import markdown2 # Pour la conversion Markdown vers HTML

def send_contact_email(name, email, message_body):
    """Envoie l'email du formulaire de contact."""
    try:
        msg = Message(
            subject=f"Nouveau message de contact de {name}",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[current_app.config['MY_PROJECT_EMAIL']],
            body=f"Nom: {name}\nEmail: {email}\nMessage:\n{message_body}"
        )
        mail.send(msg)
        return True, "Email envoyé avec succès."
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'email de contact: {e}")
        return False, f"Erreur lors de l'envoi de l'email: {str(e)}"

def send_newsletter_email(subject, html_content, recipient_email):
    """Envoie un email de newsletter individuel."""
    try:
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[recipient_email],
            html=html_content
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Erreur d'envoi newsletter à {recipient_email}: {e}")
        return False

def style_newsletter_message(markdown_text_or_html, custom_vars=None):
    """
    Style le message de la newsletter.
    Accepte du Markdown ou du HTML.
    Utilise un template Jinja2 pour un enrobage HTML de base.
    """
    if custom_vars is None:
        custom_vars = {}

    # Si c'est du Markdown, on le convertit en HTML
    # On peut ajouter des extensions markdown2 ici si besoin (ex: 'fenced-code-blocks', 'tables')
    html_body = markdown2.markdown(markdown_text_or_html, extras=["smarty-pants", "cuddled-lists", "target-blank-links"])

    # Utiliser un template Jinja2 pour l'email
    # Vous pouvez passer des variables supplémentaires au template via custom_vars
    full_html_content = render_template(
        'newsletter_template.html',
        content=html_body,
        **custom_vars # Par exemple: unsubscribe_link, company_name
    )
    return full_html_content