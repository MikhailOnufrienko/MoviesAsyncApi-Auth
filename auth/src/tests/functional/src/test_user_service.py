from typing import Any
import pytest
from auth.schemas.entity import (ChangeCredentials, SingleRole,
                                 Token, UserLogin, UserRegistration)

from auth.src.tests.conftest import client
from auth.src.services import access_logic, token_logic, user_logic
from . import parametrize, utils


@pytest.mark.parametrize('new_user, expected', parametrize.USER_TO_REGISTER)
@pytest.mark.usefixtures("create_schema", "create_tables", "create_user")
async def test_register_user(
    new_user: tuple[UserRegistration, dict[str, Any]],
    expected: tuple[UserRegistration, dict[str, Any]]
):
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


@pytest.mark.parametrize('user, expected', parametrize.USER_TO_LOGIN)
@pytest.mark.usefixtures("create_schema", "create_tables", "create_user")
async def test_login_user(
    user: tuple[UserLogin, dict[str, Any]],
    expected: tuple[UserLogin, dict[str, Any]]
):
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
    

@pytest.mark.parametrize('user_header, expected', parametrize.USER_TO_LOGOUT)
@pytest.mark.usefixtures("create_schema", "create_tables", "create_user")
async def test_logout_user(
    user_header: tuple[dict[str, str], dict[str, Any]],
    expected: tuple[dict[str, str], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(user_logic, 'logout_user', utils.mock_logout_user)
    response = client.post(
        '/api/v1/auth/user/logout',
        headers=user_header
    )
    assert response.status_code == expected['status_code']
    assert response.json() == expected['data']


@pytest.mark.parametrize('tokens, expected', parametrize.REFRESH_TOKENS)
async def test_refresh_tokens(
    tokens: tuple[Token, dict[str, Any]],
    expected: tuple[Token, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        token_logic,
        'refresh_tokens',
        utils.mock_refresh_tokens
    )
    response = client.post(
        '/api/v1/auth/user/{test_user_id}/refresh',
        json={
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token
        },
        params={'test_user_id': 'f9da64a4-c7c0-4bf2-8043-a1e725343bdf'}
    )
    assert response.json() == expected['data']
    assert response.status_code == expected['status_code']


@pytest.mark.parametrize('new_credentials, expected', parametrize.CHANGE_CREDENTIALS)
async def test_change_credentials(
    new_credentials: tuple[ChangeCredentials, dict[str, Any]],
    expected: tuple[ChangeCredentials, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        user_logic, 'change_credentials', utils.mock_change_credentials
    )
    response = client.patch(
        '/api/v1/auth/user/change_credentials',
        json={
            'new_login': new_credentials.new_login,
            'old_password': new_credentials.old_password,
            'new_password': new_credentials.new_password
        },
        headers={'authorization': 'very.secure.jwt-token555'}
    )
    assert response.json() == expected['data']
    assert response.status_code == expected['status_code']


@pytest.mark.parametrize('new_role, expected', parametrize.CREATE_ROLE)
async def test_create_role(
    new_role: tuple[SingleRole, dict[str, Any]],
    expected: tuple[SingleRole, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        access_logic, 'create_role', utils.mock_create_role
    )
    response = client.post(
        '/api/v1/auth/access/role',
        json={
            'name': new_role.name,
            'description': new_role.description
        },
        headers={'authorization': 'very.secure.jwt-token555'}
    )
    assert response.json() == expected['data']
    assert response.status_code == expected['status_code']


@pytest.mark.usefixtures('create_schema', 'create_tables', 'create_roles')
async def test_view_roles(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        access_logic, 'view_roles', utils.mock_view_roles
    )
    response = client.get(
        '/api/v1/auth/access/role',
        headers={'authorization': 'very.secure.jwt-token555'}
    )
    assert response.json() == {
        'success': [
            {'name': 'test_editor', 'description': 'description'},
            {'name': 'test_admin', 'description': 'description'}
        ]
    }
    assert response.status_code == 200


@pytest.mark.parametrize('changed_role, expected', parametrize.CHANGE_ROLE)
@pytest.mark.usefixtures('create_schema', 'create_tables', 'create_roles')
async def test_change_role(
    changed_role: tuple[SingleRole, dict[str, Any]],
    expected: tuple[SingleRole, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(
        access_logic, 'change_role', utils.mock_change_role
    )
    response = client.put(
        'api/v1/auth/access/role/{test_role_id}',
        json={
            'name': changed_role.name, 'description': changed_role.description
        },
        params={'test_role_id': 'e0b4ac52-1173-45dd-9a81-e3a915872385'},
        headers={'authorization': 'very.secure.jwt-token555'}
    )
    assert response.json() == expected['data']
    assert response.status_code == expected['status_code']
