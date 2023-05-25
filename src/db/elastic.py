from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch


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
    hosts='http://elastic_search:9200/'
)


async def get_elastic() -> AsyncElasticsearch:
    return elastic
