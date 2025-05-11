import re
from werkzeug.utils import secure_filename
from flask import current_app
import os

def is_valid_email(email):
    """Vérifie basiquement le format d'un email."""
    if not email:
        return False
    # Regex simple, peut être améliorée
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def secure_save_file(file_storage, subfolder=''):
    """Sauvegarde un fichier de manière sécurisée."""
    if file_storage and file_storage.filename:
        original_filename = file_storage.filename
        if '.' in original_filename and original_filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
            filename = secure_filename(original_filename)
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            file_path = os.path.join(upload_dir, filename)
            file_storage.save(file_path)
            return file_path, filename
    return None, None