import json
import io
from unittest.mock import patch

def test_chat_endpoint_text_only(client):
    """Teste le endpoint /chat avec une requête texte simple."""
    mock_response = {"reply": "Réponse texte simple."}
    with patch('api.routes.chat.gemini_service.generate_chat_response', return_value=mock_response) as mock_gemini:
        response = client.post('/chat', data={'message': 'Juste du texte'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['reply'] == "Réponse texte simple."
        mock_gemini.assert_called_once_with('Juste du texte', None, {})

def test_chat_endpoint_with_file(client):
    """Teste le endpoint /chat avec un message et un fichier."""
    mock_response = {"reply": "Réponse sur l'image."}
    with patch('api.routes.chat.gemini_service.generate_chat_response', return_value=mock_response) as mock_gemini, \
         patch('PIL.Image.open') as mock_pil_open:
        
        data = {
            'message': 'Que vois-tu sur cette image ?',
            'file': (io.BytesIO(b"fake_image_data"), 'test.jpg', 'image/jpeg')
        }
        
        response = client.post('/chat', content_type='multipart/form-data', data=data)
        
        assert response.status_code == 200
        mock_pil_open.assert_called_once()
        assert mock_gemini.call_args[0][1] is not None # Vérifie que file_part n'est pas None

def test_chat_endpoint_missing_message(client):
    """Teste le cas où le champ 'message' est manquant."""
    response = client.post('/chat', data={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
