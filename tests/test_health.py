import json

def test_health_check(client):
    """Teste le endpoint /health."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'services' in data
    assert data['services']['flask'] == 'healthy'
