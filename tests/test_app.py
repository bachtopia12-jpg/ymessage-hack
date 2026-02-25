import pytest
import os

# On s'assure que la DB n'est pas un problème pour le test
os.environ['DATABASE'] = ':memory:'

from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Vérifie que la page d'accueil (register) est accessible"""
    res = client.get('/')
    assert res.status_code in [200, 302]

def test_login_page(client):
    """Vérifie que la page de login est accessible"""
    res = client.get('/login')
    assert res.status_code == 200
