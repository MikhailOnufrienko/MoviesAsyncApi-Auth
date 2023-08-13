import pytest

from auth.schemas.entity import Token, UserLogin, UserRegistration
from auth.src.tests.conftest import client
from . import parametrize


@pytest.mark.parametrize(
        'new_user, expected',
        parametrize.USER_TO_REGISTER
)
@pytest.mark.usefixtures("create_schema", "prepare_db", "create_user")
async def test_register_user(new_user, expected):
    response = client.post(
        '/api/v1/auth/user/register',
        json = {
            'login': new_user.login,
            'password': new_user.password,
            'email': new_user.email
        },
    )
    data = response.json()
    assert response.status_code == expected.get('status_code'), response.text
    assert data == expected.get('data')


# def test_login_exists():
#     user = UserRegistration(
#         login='descartes', password='cogitoergosum', email='descartes@ratio.org'
#     )
#     response = client.post(
#         '/api/v1/auth/user/register',
#         json = {
#             'login': user.login,
#             'email': user.email,
#             'password': user.password
#         },
#     )
#     assert response.status_code == 400
#     assert response.json() == {
#         'detail': 'Пользователь с таким логином уже зарегистрирован.'
#     }


# def test_email_exists():
#     user = UserRegistration(
#         login='stevenpinker', password='violencedeclines', email='descartes@ratio.org'
#     )
#     response = client.post(
#         '/api/v1/auth/user/register',
#         json = {
#             'login': user.login,
#             'email': user.email,
#             'password': user.password
#         },
#     )
#     assert response.status_code == 400
#     assert response.json() == {
#         'detail': 'Пользователь с таким email уже зарегистрирован.'
#     }


# def test_password_is_incorrect():
#     user = UserLogin(login='descartes', password='wrongpassword')
#     response = client.post(
#         '/api/v1/auth/user/login',
#         json = {
#             'login': user.login,
#             'password': user.password
#         }
#     )
#     assert response.status_code == 401, response.text
#     assert response.json() == {'detail': 'Логин или пароль не верен.'}


# def test_login_user():
#     user = UserLogin(login='descartes', password='cogitoergosum')
#     response = client.post(
#         '/api/v1/auth/user/login',
#         json = {
#             'login': user.login,
#             'password': user.password
#         }
#     )
#     data = response.json()
#     assert response.status_code == 200, response.text
#     assert data == 'Вы вошли в свою учётную запись.'
#     assert 'X-Access-Token' in response.headers
#     assert 'X-Refresh-Token' in response.headers


# def test_logout_user(login_user):
#     acc, ref = login_user
#     tokens = Token(
#             access_token=acc,
#             refresh_token=ref
#     )
#     response = client.post(
#         '/api/v1/auth/user/logout',
#         json = {'access_token': tokens.access_token,
#                 'refresh_token': tokens.refresh_token}
#     )
#     data = response.json()
#     assert response.status_code == 200, response.text
#     assert data == 'Вы вышли из учётной записи.'


# @pytest.fixture
# def login_user():
#     # response = client.post(
#     #     '/api/v1/auth/user/login',
#     #     json = {
#     #         'login': 'descartes',
#     #         'password': 'cogitoergosum'
#     #     }
#     # )
#     access_token = '1233qwed12as'
#     refresh_token = '123qgwe12ads'
#     yield (access_token, refresh_token)
    