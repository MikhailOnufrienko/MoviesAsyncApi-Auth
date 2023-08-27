from typing import Annotated
from fastapi import Depends
from redis.asyncio import client

from auth.src.core.config import app_settings

redis: client.Redis = client.Redis(
    host=app_settings.REDIS_HOST,
    port=app_settings.REDIS_PORT,
    db=app_settings.REDIS_DB
)
async def get_redis() -> client.Redis:
    return redis


REDIS_DEPEND = Annotated[client.Redis, Depends(get_redis)]
