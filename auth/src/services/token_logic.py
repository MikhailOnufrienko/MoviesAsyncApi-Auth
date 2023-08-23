from datetime import datetime, timedelta
from typing import Annotated
from fastapi import HTTPException, Header

from jose import jwt
from redis.asyncio import client

from auth.src.core.config import app_settings
from auth.src.core.config import app_settings


async def generate_tokens(user_id: str) -> tuple[str]:
    subject_id = {'sub': user_id}
    access_token = await generate_access_token(
        subject_id, app_settings.ACCESS_TOKEN_EXPIRES_IN
    )
    refresh_token = await generate_refresh_token(
        subject_id, app_settings.REFRESH_TOKEN_EXPIRES_IN
    )
    return access_token, refresh_token


async def generate_access_token(data: dict, expires_delta: int) -> str:
    to_encode = await prepare_data_for_generating_tokens(
        data, expires_delta
    )
    encoded_jwt = jwt.encode(
        to_encode, app_settings.ACCESS_JWT_SECRET_KEY,
        algorithm = app_settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def generate_refresh_token(data: dict, expires_delta: int) -> str:
    to_encode = await prepare_data_for_generating_tokens(
        data, expires_delta
    )
    encoded_jwt = jwt.encode(
        to_encode, app_settings.REFRESH_JWT_SECRET_KEY,
        algorithm = app_settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def prepare_data_for_generating_tokens(
    data: dict, expires_delta: int
) -> dict:
    to_encode = data.copy()
    expire_in_days = datetime.utcnow() + timedelta(days=expires_delta)
    to_encode.update({'exp': expire_in_days})
    return to_encode


async def save_refresh_token_to_cache(
    user_id: str, token: str, cache: client.Redis
) -> None:
    expires: int = app_settings.REFRESH_TOKEN_EXPIRES_IN  * 24 * 60 * 60
    await cache.setex(user_id, expires, token)


async def delete_refresh_token_from_cache(
    cache: client.Redis, user_id: str
) -> None:
    await cache.delete(user_id)


async def add_invalid_access_token_to_cache(
    access_token: str, cache: client.Redis
) -> None:
    current_datetime = datetime.now()
    invalid_token_key = f'invalid:{current_datetime}'
    expires: int = app_settings.ACCESS_TOKEN_EXPIRES_IN * 24 * 60 * 60
    await cache.setex(invalid_token_key, expires, access_token)


async def get_user_id_by_token(access_token: str) -> str:
    claims = jwt.get_unverified_claims(access_token)
    return claims['sub']


async def refresh_tokens(
    user_id: str, old_access_token: str, old_refresh_token: str, cache: client.Redis
) -> dict:
    if await check_old_token_equal_stored_token(user_id, old_refresh_token, cache):
        new_access_token, new_refresh_token = await generate_tokens(user_id)
        await save_refresh_token_to_cache(user_id, new_refresh_token, cache)
        await add_invalid_access_token_to_cache(old_access_token, cache)
        return {'access': new_access_token, 'refresh': new_refresh_token}
    return {'error': 'Недействительный refresh-токен. Требуется пройти аутентификацию.'}
    

async def check_old_token_equal_stored_token(
        user_id: str, old_token: str, cache: client.Redis
) -> bool:
    stored_token: bytes = await cache.get(user_id)
    if not stored_token or stored_token.decode() != old_token:
        return False
    return True


async def get_token_authorization(authorization: Annotated[str, Header()]) -> dict:
    if not authorization:
        return {'error': 'Отсутствует токен. Авторизуйтесь снова.'}
    try:
        scheme, token = authorization.split(' ')
        if scheme.lower() != 'bearer':
            return {'error': 'Недействительная схема авторизации. Авторизуйтесь снова.'}
        return {'success': 'Вы вышли из учётной записи.'}
    except Exception:
        return {'error': 'Недействительный токен. Авторизуйтесь снова.'}
