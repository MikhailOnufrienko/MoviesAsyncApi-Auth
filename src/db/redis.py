from abc import ABC, abstractmethod

from redis.asyncio import Redis


class AsyncCacheInterface(ABC):
    @abstractmethod
    async def get_cache_connection(self):
        pass


class AsyncCacheImplementation(AsyncCacheInterface):
    async def get_cache_connection(self):
        return Redis()


async def main():
    cache_implementation = AsyncCacheImplementation()
    conn = await cache_implementation.get_cache_connection()
    return conn

redis = AsyncCacheImplementation()
