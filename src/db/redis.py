from abc import ABC

from redis.asyncio import Redis


class AsyncCacheAbstract(ABC):
    pass


redis: Redis = Redis()

async def get_redis() -> Redis:
    return redis
