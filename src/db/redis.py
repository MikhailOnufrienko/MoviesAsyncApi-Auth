from abc import ABC

from redis.asyncio import Redis


class AsyncCacheAbstract(ABC):
    async def _get_single_object(self):
        pass

    async def _get_list_of_objects(self):
        pass

    async def _put_single_object(self):
        pass

    async def _put_list_of_objects(self):
        pass


redis: Redis = Redis()

async def get_redis() -> Redis:
    return redis
