from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch

from core.config import settings


class AsyncSearchAbstract(ABC):
    """An abstract class for retrieving data from a search service.

    """

    @abstractmethod
    async def _get_single_object(self):
        pass

    @abstractmethod
    async def _get_list_of_objects(self):
        pass


elastic: AsyncElasticsearch = AsyncElasticsearch(
    [{
        'scheme': settings.ELASTIC_SCHEME,
        'host': settings.ELASTIC_HOST,
        'port': settings.ELASTIC_PORT
    }]
)


async def get_elastic() -> AsyncElasticsearch:
    return elastic
