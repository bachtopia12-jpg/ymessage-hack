import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_redirect(client):
    """Vérifie que la racine redirige vers le login ou s'affiche (dépend de ta logique)"""
    res = client.get('/')
    assert res.status_code == 200

def test_login_page(client):
    """Vérifie que la page de login est accessible"""
    res = client.get('/login')
    assert res.status_code == 200
    assert b"Login" in res.data or b"Connexion" in res.data
