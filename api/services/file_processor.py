import PyPDF2
import docx
import io

class FileProcessor:
    def extract_text(self, file_obj, file_type):
        """Extrait le texte d'un fichier en fonction de son type."""
        file_obj.seek(0) # S'assurer que le curseur est au début du fichier
        if file_type == 'application/pdf':
            return self._extract_text_from_pdf(file_obj)
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return self._extract_text_from_docx(file_obj)
        # L'OCR pour les images sera ajouté ici plus tard
        else:
            return {"error": f"Type de fichier non supporté: {file_type}"}

    def _extract_text_from_pdf(self, file_obj):
        try:
            reader = PyPDF2.PdfReader(file_obj)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return {"text": text}
        except Exception as e:
            return {"error": f"Erreur lors de la lecture du PDF: {e}"}

    def _extract_text_from_docx(self, file_obj):
        try:
            document = docx.Document(io.BytesIO(file_obj.read()))
            text = "\n".join([para.text for para in document.paragraphs])
            return {"text": text}
        except Exception as e:
            return {"error": f"Erreur lors de la lecture du DOCX: {e}"}

file_processor = FileProcessor()
