from typing import Annotated

from fastapi import Header
from redis.asyncio import client


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
) -> bool:
    if 'good' in refresh_token:
        return {'access': 'new_access_token', 'refresh': 'new_refresh_token'}
    return {'error': 'Недействительный refresh-токен. Требуется пройти аутентификацию.'}