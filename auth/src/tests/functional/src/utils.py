from typing import Annotated

from fastapi import Header
from redis.asyncio import client


async def mock_logout_user(authorization: Annotated[str, Header()], cache: client.Redis):
    if not authorization or authorization == '':
        return {'error': 'Отсутствует токен. Авторизуйтесь снова.'}
    try:
        scheme, token = authorization.split(' ')
        if scheme.lower() != 'bearer':
            return {'error': 'Недействительная схема авторизации. Авторизуйтесь снова.'}
        return {'success': 'Вы вышли из учётной записи.'}
    except Exception:
        return {'error': 'Недействительный токен. Авторизуйтесь снова.'}
    