from markdown2 import markdown
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from io import BytesIO
from flask import current_app

class PDFService:
    def generate_pdf_from_markdown(self, markdown_content: str, custom_css: str = None) -> BytesIO:
        """
        Génère un PDF à partir d'un contenu Markdown.
        Permet d'ajouter du CSS personnalisé.
        """
        try:
            # Convertir Markdown en HTML
            # Vous pouvez ajouter des 'extras' à markdown2 si nécessaire
            # ex: extras=['fenced-code-blocks', 'tables', 'footnotes']
            html_content = markdown(markdown_content, extras=['tables', 'fenced-code-blocks', 'cuddled-lists', 'smarty-pants'])

            # Configuration des polices pour WeasyPrint (facultatif mais peut aider pour les caractères spéciaux)
            font_config = FontConfiguration()
            
            # Styles CSS de base (vous pouvez les externaliser ou les rendre plus complexes)
            base_css = """
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: 'Arial', sans-serif; /* WeasyPrint cherchera des polices système */
                    line-height: 1.5;
                    color: #333;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #1a1a1a;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }
                h1 { font-size: 2.5em; border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
                h2 { font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
                h3 { font-size: 1.75em; }
                p { margin-bottom: 1em; }
                a { color: #007bff; text-decoration: none; }
                a:hover { text-decoration: underline; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 1em;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th { background-color: #f2f2f2; }
                pre {
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    padding: 10px;
                    overflow-x: auto; /* Gérer les lignes de code longues */
                    font-family: 'Courier New', monospace;
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
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
            """
            
            stylesheets = [CSS(string=base_css)]
            if custom_css:
                stylesheets.append(CSS(string=custom_css))

            # Générer le PDF en mémoire
            pdf_file = BytesIO()
            HTML(string=html_content).write_pdf(
                pdf_file,
                stylesheets=stylesheets,
                font_config=font_config
            )
            pdf_file.seek(0) # Remettre le curseur au début du buffer
            return pdf_file, None
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la génération du PDF: {e}")
            return None, str(e)