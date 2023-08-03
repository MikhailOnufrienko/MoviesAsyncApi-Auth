import pytest
from fastapi import HTTPException

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


# def test_login_user():
#     response = client.post(
#         '/api/v1/auth/user/login',
#         json = {
#             'login': 'descartes',
#             'password': 'cogitoergosum'
#         }
#     )
#     data = response.json()
#     assert response.status_code == 200, response.text
#     assert data == 'Вы вошли в свою учётную запись.'
