import pytest

from auth.schemas.entity import Token, UserLogin, UserRegistration
from auth.src.tests.conftest import client
from . import parametrize


@pytest.mark.parametrize(
        'new_user, expected',
        parametrize.USER_TO_REGISTER
)
@pytest.mark.usefixtures("create_schema", "create_tables", "create_user")
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


@pytest.mark.parametrize(
        'user, expected',
        parametrize.USER_TO_LOGIN
)
@pytest.mark.usefixtures("create_schema", "create_tables", "create_user")
def test_login_user(user, expected):
    response = client.post(
        '/api/v1/auth/user/login',
        json = {
            'login': user.login,
            'password': user.password
        }
    )
    data = response.json()
    assert response.status_code == expected.get('status_code'), response.text
    assert data == expected.get('data')
    if response.status_code == 200:
        assert 'X-Access-Token' in response.headers 
        assert 'X-Refresh-Token' in response.headers


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
    