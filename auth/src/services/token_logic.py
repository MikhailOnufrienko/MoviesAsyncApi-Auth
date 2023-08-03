from datetime import datetime, timedelta

from jose import jwt
from redis.asyncio import client
from sqlalchemy import select
from sqlalchemy import insert

from auth.src.core.config import app_settings
from auth.src.db.redis import get_redis
from auth.src.models.entity import User, Role, UserProfile
from auth.src.db.postgres import AsyncSession
from auth.src.core.config import app_settings


default_role_name: str = 'registered user'


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
    

async def fill_in_user_profile_table(db: AsyncSession, user: User) -> None:
    query_for_default_role = select(Role.id).filter(Role.name == default_role_name)
    result = await db.execute(query_for_default_role)
    default_role_id = result.scalar_one_or_none()
    if default_role_id:
        user_profile_table = UserProfile.__table__
        insert_query = (
            insert(user_profile_table).values(user_id=user.id, role_id=default_role_id)
        )
        await db.execute(insert_query)
    await db.commit()
