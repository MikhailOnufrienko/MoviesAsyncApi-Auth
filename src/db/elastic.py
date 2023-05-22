from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch


class AsyncSearchAbstract(ABC):
    pass


elastic: AsyncElasticsearch = AsyncElasticsearch(hosts='http://localhost:9200/')

async def get_elastic() -> AsyncElasticsearch:
    return elastic
