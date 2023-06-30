from datetime import datetime, timedelta

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.schemas.entity import RefreshToken
from redis.asyncio import client

from auth.src.core.config import app_settings
from auth.src.db.redis import get_redis



async def generate_access_token(data: dict, expires_delta: int) -> str:
    to_encode = data.copy()
    expire_in_days = datetime.utcnow() + timedelta(days=expires_delta)
    to_encode.update({'exp': expire_in_days})
    encoded_jwt = jwt.encode(to_encode, app_settings.ACCESS_JWT_SECRET_KEY, algorithm=app_settings.JWT_ALGORITHM)
    return encoded_jwt


async def generate_refresh_token(data: dict, expires_delta: int) -> str:
    to_encode = data.copy()
    expire_in_days = datetime.utcnow() + timedelta(days=expires_delta)
    to_encode.update({'exp': expire_in_days})
    encoded_jwt = jwt.encode(to_encode, app_settings.REFRESH_JWT_SECRET_KEY, algorithm=app_settings.JWT_ALGORITHM)
    return encoded_jwt


async def save_refresh_token_to_cache(user_id: str, token: str) -> None:
    cache: client.Redis = await get_redis()
    if await check_refresh_token_exists_in_cache(cache, user_id):
        await delete_refresh_token_from_cache(cache, user_id)
    expires: int = app_settings.REFRESH_TOKEN_EXPIRES_IN * 60 * 60 * 24
    await cache.setex(user_id, expires, token)


async def check_refresh_token_exists_in_cache(cache: client.Redis, user_id: str) -> bool:
    old_token = await cache.get(user_id)
    if old_token:
        return True
    return False


async def delete_refresh_token_from_cache(cache: client.Redis, user_id: str) -> None:
    cache.delete(user_id)