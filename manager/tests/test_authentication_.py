import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def test_user():
    username = 'testuser'
    password = 'testpassword'
    user = User.objects.create_user(username=username, password=password)
    yield user
    user.delete()

@pytest.mark.django_db
def test_login_valid_user(client, test_user):
    # Simuler une demande POST avec des identifiants valides
    login_data = {
        'username': test_user.username,
        'password': 'testpassword',  # Mot de passe correct
    }
    response = client.post(reverse('loginUser'), data=login_data)

    # Vérifier si le code d'état de la réponse est 302 (redirection après une connexion réussie)
    assert response.status_code == 302

    # Vérifier si l'utilisateur est maintenant connecté
    assert client.login(username=test_user.username, password='testpassword')

@pytest.mark.django_db
def test_login_invalid_user(client):
    # Simuler une demande POST avec des identifiants invalides
    login_data = {
        'username': 'invaliduser',
        'password': 'invalidpassword',
    }
    response = client.post(reverse('loginUser'), data=login_data)

    # Vérifier si le code d'état de la réponse est 200 (OK)
    assert response.status_code == 200
