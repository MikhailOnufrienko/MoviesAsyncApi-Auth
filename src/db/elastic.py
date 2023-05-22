from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch


class AsyncSearchFilmAbstract(ABC):
    @abstractmethod
    async def _get_film_from_elastic(self, film_id: str):
        pass

    @abstractmethod
    async def _get_films_from_elastic(self, search_query: dict):
        pass


class AsyncSearchGenreAbstract(ABC):
    @abstractmethod
    async def _get_genre_from_elastic(self, film_id: str):
        pass

    @abstractmethod
    async def _get_genres_from_elastic(self, search_query: dict):
        pass


elastic: AsyncElasticsearch = AsyncElasticsearch(hosts='http://localhost:9200/')

async def get_elastic() -> AsyncElasticsearch:
    return elastic
