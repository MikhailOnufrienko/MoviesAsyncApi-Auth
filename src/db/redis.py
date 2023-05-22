from abc import ABC

from redis.asyncio import Redis


class AsyncCacheAbstract(ABC):
#    @abstractmethod
#    async def get_cache_connection(self):
        pass


#class AsyncCacheImplementation(AsyncCacheInterface):
#    def __init__(self, redis):
#        self.redis = redis

#    async def get_cache_connection(self):
#        return Redis()


redis: Redis = Redis()

async def get_redis() -> Redis:
    return redis


#async def main():
#    cache_implementation = AsyncCacheImplementation()
#    conn = await cache_implementation.get_cache_connection()
#    return conn

#redis = AsyncCacheImplementation()
