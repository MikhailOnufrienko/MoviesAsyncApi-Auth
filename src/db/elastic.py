from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch


class AsyncSearchInterface(ABC):
    @abstractmethod
    async def get_search_connection(self):
        pass

    
class AsyncSearchImplementation(AsyncSearchInterface):
    async def get_search_connection(self):
        return AsyncElasticsearch()


async def main():
    search_implementation = AsyncSearchImplementation()
    es = search_implementation.get_search_connection()
    return es

es = AsyncSearchImplementation()
