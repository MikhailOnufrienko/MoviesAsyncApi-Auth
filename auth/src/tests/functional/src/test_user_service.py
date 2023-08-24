from fastapi.responses import JSONResponse
import pytest

from auth.schemas.entity import Token, UserLogin, UserRegistration
from auth.src.tests.conftest import client
from auth.src.services import token_logic, user_logic
from . import parametrize, utils


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
async def test_login_user(user, expected):
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
    

@pytest.mark.parametrize(
        'user_header, expected',
        parametrize.USER_TO_LOGOUT
)
@pytest.mark.usefixtures("create_schema", "create_tables", "create_user")
async def test_logout_user(user_header, expected, monkeypatch):
    monkeypatch.setattr(user_logic, 'logout_user', utils.mock_logout_user)
    response = client.post(
        '/api/v1/auth/user/logout',
        headers=user_header
    )
    assert response.status_code == expected['status_code']
    assert response.json() == expected['data']


@pytest.mark.parametrize(
        'tokens, expected',
        parametrize.REFRESH_TOKENS
)
async def test_refresh_tokens(tokens, expected, monkeypatch):
    monkeypatch.setattr(
        token_logic,
        'refresh_tokens',
        utils.mock_refresh_tokens
    )
    test_user_id = 'f9da64a4-c7c0-4bf2-8043-a1e725343bdf'
    response = client.post(
        f'/api/v1/auth/user/{test_user_id}/refresh',
        json={
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token
        }
    )
    assert response.json() == expected['data']
    assert response.status_code == expected['status_code']


@pytest.mark.parametrize(
        'new_credentials, expected',
        parametrize.CHANGE_CREDENTIALS
)
async def test_change_credentials(new_credentials, expected):
    response = client.put(
        '/api/v1/auth/user/change_credentials',
        json={
            'new_login': new_credentials.new_login,
            'old_password': new_credentials.old_password,
            'new_password': new_credentials.new_password
        }
    )
    assert response.json() == expected['data']
    assert response.status_code == expected['status_code']
