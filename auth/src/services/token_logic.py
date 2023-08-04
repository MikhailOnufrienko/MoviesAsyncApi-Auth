from datetime import datetime, timedelta

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
