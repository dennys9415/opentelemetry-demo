import pytest
import json
from src.backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'backend'

def test_get_users(client):
    """Test getting users"""
    response = client.get('/api/users')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

def test_create_user(client):
    """Test creating a user"""
    user_data = {
        'name': 'Test User',
        'email': 'test@example.com'
    }
    response = client.post('/api/users', 
                         data=json.dumps(user_data),
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data
    assert data['name'] == user_data['name']
    assert data['email'] == user_data['email']

def test_get_products(client):
    """Test getting products"""
    response = client.get('/api/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_create_order(client):
    """Test creating an order"""
    order_data = {
        'product_id': 1,
        'quantity': 2
    }
    response = client.post('/api/order',
                         data=json.dumps(order_data),
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'order_id' in data
    assert data['status'] == 'completed'