import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.testclient import TestClient

from app.main import app
from app.services.recommendation_service import RecommendationService


client = TestClient(app)


def test_early_blight_recommendations_include_actionable_steps():
    plan = RecommendationService().get_recommendations('Early Blight', 'Tomato')

    assert plan['crop'] == 'Tomato'
    assert len(plan['action_plan']) >= 3
    assert all(phase['timing'] and phase['steps'] for phase in plan['action_plan'])
    assert 'not a confirmed diagnosis' in plan['safety_note']
    assert any('registered' in item for item in plan['recommendations'])


def test_register_and_login():
    unique_email = 'tester@example.com'
    response = client.post('/api/v1/auth/register', data={'name': 'Test Farmer', 'email': unique_email, 'password': 'secret123', 'location': 'Patna'})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['message'] == 'Farmer registered successfully'

    login = client.post('/api/v1/auth/login', data={'email': unique_email, 'password': 'secret123'})
    assert login.status_code == 200, login.text
    token = login.json()['access_token']
    assert token

    me = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200, me.text
    assert me.json()['user']['email'] == unique_email


def test_detect_disease_returns_model_status():
    login = client.post('/api/v1/auth/login', data={'email': 'farmer@demo.com', 'password': 'password123'})
    token = login.json()['access_token']

    image_buffer = io.BytesIO()
    from PIL import Image
    Image.new('RGB', (64, 64), color='green').save(image_buffer, format='PNG')
    image_buffer.seek(0)

    response = client.post(
        '/api/v1/diagnoses/detect',
        files={'file': ('leaf.png', image_buffer.getvalue(), 'image/png')},
        data={'crop_name': 'Tomato', 'location': 'Patna'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['prediction']['prediction_status'] in {'model_unavailable', 'predicted'}
    assert 'message' in body['prediction']


def test_admin_dashboard():
    login = client.post('/api/v1/auth/login', data={'email': 'admin@cropshield.ai', 'password': 'admin123'})
    token = login.json()['access_token']
    response = client.get('/api/v1/admin/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200, response.text
    data = response.json()
    assert 'summary' in data
    assert 'total_farmers' in data['summary']
    assert 'hotspots' in data
    assert 'expert_queue' in data
