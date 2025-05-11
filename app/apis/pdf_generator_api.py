from flask import request, current_app, send_file
from flask_restx import Namespace, Resource, fields
import io

from app.services.pdf_service import PDFService
from .models import pdf_input_model, error_response_model
from app.extensions import limiter

ns = Namespace('PDF Generator', description='Conversion de Markdown en PDF')

# Modèles
pdf_input = ns.model('PDFInput', pdf_input_model)
error_resp = ns.model('ErrorResponsePDF', error_response_model)

@ns.route('/markdown-to-pdf')
class MarkdownToPDFResource(Resource):
    # @ns.doc(security='apikey')
    @ns.expect(pdf_input)
    @ns.response(200, 'PDF généré avec succès (fichier binaire).')
    @ns.response(400, 'Données d\'entrée invalides', error_resp)
    @ns.response(500, 'Erreur lors de la génération du PDF', error_resp)
    @limiter.limit("30 per hour")
    def post(self):
        """
        Convertit un texte Markdown fourni en un fichier PDF.
        Retourne le fichier PDF directement dans la réponse.
        """
        data = ns.payload
        markdown_content = data.get('markdown_content')
        custom_css = data.get('custom_css')

        if not markdown_content:
            return {'status': 'error', 'message': 'Le champ "markdown_content" est requis.'}, 400

        pdf_service = PDFService()
        pdf_buffer, error = pdf_service.generate_pdf_from_markdown(markdown_content, custom_css)

        if error:
            current_app.logger.error(f"Erreur PDF generation: {error}")
            return {'status': 'error', 'message': f"Erreur lors de la génération du PDF: {error}"}, 500

        if pdf_buffer:
            current_app.logger.info("PDF généré avec succès à partir de Markdown.")
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name='rapport_genere.pdf',
                mimetype='application/pdf'
            )
        else:
            # Ce cas ne devrait pas être atteint si error est None, mais par sécurité.
            return {'status': 'error', 'message': 'Erreur inconnue lors de la génération du PDF.'}, 500