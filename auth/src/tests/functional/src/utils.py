from typing import Annotated

from fastapi import Header
from redis.asyncio import client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth.schemas.entity import ChangeCredentials, SingleRole
from auth.src.models.entity import Role
from auth.src.services.access_logic import get_role_by_id_or_return_false


async def mock_logout_user(
    authorization: Annotated[str, Header()], cache: client.Redis
) -> dict:
    if not authorization or authorization == '':
        return {'error': 'Отсутствует токен. Авторизуйтесь снова.'}
    try:
        scheme, token = authorization.split(' ')
        if scheme.lower() != 'bearer':
            return {'error': 'Недействительная схема авторизации. Авторизуйтесь снова.'}
        return {'success': 'Вы вышли из учётной записи.'}
    except Exception:
        return {'error': 'Недействительный токен. Авторизуйтесь снова.'}


async def mock_refresh_tokens(
    user_id: str, access_token: str, refresh_token: str, cache: client.Redis
) -> dict:
    if 'good' in refresh_token:
        return {'access': 'new_access_token', 'refresh': 'new_refresh_token'}
    return {'error': 'Недействительный refresh-токен. Требуется пройти аутентификацию.'}


async def mock_change_credentials(
    credentials: ChangeCredentials,
    authorization: Annotated[str, Header()],
    db: AsyncSession,
    cache: client.Redis
) -> dict:
    if 'wrong' in credentials.old_password:
        return {'pass_error': 'Неверный старый пароль.'}
    if 'existing' in credentials.new_login:
        return {'login_error': 'Указанный новый логин уже существует в системе.'}
    return {'success': 'Данные успешно изменены.'}


async def mock_create_role(
    role: Role, authorization: Annotated[str, Header()], db: AsyncSession
) -> dict:
    if 'no_access' in role.name:
        return {'access_error': 'Отсутствуют необходимые права доступа.'}
    return {'success': 'Роль успешно создана.'}


async def mock_view_roles(
    authorization: Annotated[str, Header()], db: AsyncSession
) -> dict:
    query = select(Role.name, Role.description)
    result = await db.execute(query)
    roles = result.fetchall()
    return {
        'success': [
            {'name': name, 'description': description} for name, description in roles
        ]
    }


async def mock_change_role(
    role_id: str, new_role_data: SingleRole,
    authorization: Annotated[str, Header()], db: AsyncSession
) -> dict:
    if 'no_access' in new_role_data.name:
        return {'access_error': 'Отсутствуют необходимые права доступа.'}
    if 'not_exists' in new_role_data.name:
        return {'not_found_error': 'Роль не найдена.'}
    return {
        'success': {
            'name': new_role_data.name,
            'description': new_role_data.description
        }
    }
