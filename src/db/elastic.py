from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch


class AsyncSearchAbstract(ABC):
 #   @abstractmethod
  #  async def get_search_connection(self):
        pass

    
#class AsyncSearchImplementation(AsyncSearchInterface):
#    def __init__(self, elastic):
#        self.elastic = elastic


elastic: AsyncElasticsearch = AsyncElasticsearch(hosts='http://localhost:9200/')

async def get_elastic() -> AsyncElasticsearch:
    return elastic

#async def main():
#    search_implementation = AsyncSearchImplementation()
#    es = search_implementation.get_search_connection()
#    return es

#es = AsyncSearchImplementation()
