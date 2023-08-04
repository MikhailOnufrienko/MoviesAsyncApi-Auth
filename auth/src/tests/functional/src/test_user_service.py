import pytest

from auth.schemas.entity import Token, UserLogin, UserRegistration
from auth.src.tests.conftest import client


def test_register_user():
    response = client.post(
        '/api/v1/auth/user/register',
        json = {
            'login': 'descartes',
            'email': 'descartes@ratio.org',
            'password': 'cogitoergosum'
        },
    )
    data = response.json()
    assert response.status_code == 201, response.text
    assert data == 'Вы успешно зарегистрировались.'


def test_login_exists():
    response = client.post(
        '/api/v1/auth/user/register',
        json = {
            'login': 'descartes',
            'email': 'descartes@ratio.org',
            'password': 'cogitoergosum'
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Пользователь с таким логином уже зарегистрирован.'
    }


def test_email_exists():
    response = client.post(
        '/api/v1/auth/user/register',
        json = {
            'login': 'stevenpinker',
            'email': 'descartes@ratio.org',
            'password': 'violencedeclines'
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Пользователь с таким email уже зарегистрирован.'
    }


def test_password_is_incorrect():
    response = client.post(
        '/api/v1/auth/user/login',
        json = {
            'login': 'descartes',
            'password': 'wrongpassword'
        }
    )
    assert response.status_code == 401, response.text
    assert response.json() == {'detail': 'Логин или пароль не верен.'}


def test_login_user():
    response = client.post(
        '/api/v1/auth/user/login',
        json = {
            'login': 'descartes',
            'password': 'cogitoergosum'
        }
    )
    data = response.json()
    assert response.status_code == 200, response.text
    assert data == 'Вы вошли в свою учётную запись.'
    assert 'X-Access-Token' in response.headers
    assert 'X-Refresh-Token' in response.headers


def test_logout_user(login_user):
    acc, ref = login_user
    tokens = Token(
            access_token=acc,
            refresh_token=ref
    )
    response = client.post(
        '/api/v1/auth/user/logout',
        json = {'access_token': tokens.access_token,
                'refresh_token': tokens.refresh_token}
    )
    data = response.json()
    assert response.status_code == 200, response.text
    assert data == 'Вы вышли из учётной записи.'


@pytest.fixture
def login_user():
    response = client.post(
        '/api/v1/auth/user/login',
        json = {
            'login': 'descartes',
            'password': 'cogitoergosum'
        }
    )
    access_token = response.headers['X-Access-Token']
    refresh_token = response.headers['X-Refresh-Token']
    return [access_token, refresh_token]
