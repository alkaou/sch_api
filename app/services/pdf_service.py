# app/services/pdf_service.py

from markdown2 import markdown
from weasyprint import HTML, CSS
# Suppression de l'import de FontConfiguration car il cause une erreur
# from weasyprint import FontConfiguration
from io import BytesIO
from flask import current_app

class PDFService:
    def generate_pdf_from_markdown(self, markdown_content: str, custom_css: str = None) -> tuple[BytesIO | None, str | None]:
        """
        Génère un PDF à partir d'un contenu Markdown.
        Permet d'ajouter du CSS personnalisé.
        Retourne un tuple (BytesIO, None) en cas de succès, ou (None, str) en cas d'erreur.
        """
        try:
            # Convertir Markdown en HTML
            html_content = markdown(markdown_content, extras=['tables', 'fenced-code-blocks', 'cuddled-lists', 'smarty-pants', 'target-blank-links'])

            # Suppression de l'instanciation explicite de FontConfiguration
            # font_config = FontConfiguration()

            # Styles CSS de base
            base_css = """
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: 'Arial', sans-serif;
                    line-height: 1.5;
                    color: #333;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #1a1a1a;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                    page-break-after: avoid;
                }
                h1 { font-size: 2.5em; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
                h2 { font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
                h3 { font-size: 1.75em; }
                p { margin-bottom: 1em; text-align: justify; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 1em;
                    page-break-inside: avoid;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th { background-color: #f2f2f2; font-weight: bold; }
                pre {
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    padding: 10px;
                    overflow-x: auto;
                    font-family: 'Courier New', monospace;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    page-break-inside: avoid;
                }
                code {
                    font-family: 'Courier New', monospace;
                    background-color: #f0f0f0;
                    padding: 0.2em 0.4em;
                    border-radius: 3px;
                }
                blockquote {
                    border-left: 4px solid #ccc;
                    padding-left: 1em;
                    margin-left: 0;
                    color: #555;
                    font-style: italic;
                    page-break-inside: avoid;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 1em auto;
                    page-break-inside: avoid;
                }
                ul, ol {
                     margin-bottom: 1em;
                     padding-left: 1.5em;
                }
                li {
                     margin-bottom: 0.5em;
                }
            """

            stylesheets = [CSS(string=base_css)]
            if custom_css:
                stylesheets.append(CSS(string=custom_css))

            # Générer le PDF en mémoire
            pdf_file = BytesIO()
            html_doc = HTML(string=html_content, base_url='.')

            # Écrire le PDF sans passer explicitement font_config
            # WeasyPrint utilisera sa configuration de police par défaut.
            html_doc.write_pdf(
                target=pdf_file,
                stylesheets=stylesheets
                # font_config=font_config # Ligne supprimée
            )

            pdf_file.seek(0)
            return pdf_file, None
        except Exception as e:
            # Log détaillé de l'erreur (très important pour le débogage de WeasyPrint)
            current_app.logger.error(f"Erreur WeasyPrint lors de la génération du PDF: {e}", exc_info=True)
            return None, f"Erreur lors de la génération PDF: {e}"