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
