from abc import ABC, abstractmethod

from redis.asyncio import Redis


class AsyncCacheAbstract(ABC):
    """An abstract class for sending data to
       and retrieving data from a cache service.

    """
    @abstractmethod
    async def _get_single_object(self):
        pass

    @abstractmethod
    async def _get_list_of_objects(self):
        pass

    @abstractmethod
    async def _put_single_object(self):
        pass

    @abstractmethod
    async def _put_list_of_objects(self):
        pass


redis: Redis = Redis()


async def get_redis() -> Redis:
    return redis
