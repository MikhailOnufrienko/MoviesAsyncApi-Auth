import json
from functools import lru_cache
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import FilmFull, FilmShort

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 minutes

INDEX_NAME = 'movies'


class FilmService:
    """Class to represent films logic."""

    def __init__(
        self,
        redis: Redis,
        elastic: AsyncElasticsearch,
        index_name: str
    ):
        self.redis = redis
        self.elastic = elastic
        self.index_name = index_name

    async def get_films(
            self,
            page: int,
            size: int,
            genre: UUID
    ) -> tuple[int, list[FilmShort]]:
        """Retrieve films instances to list films
        in accordance with filtration conditions.

        """
        total, films = await self._films_from_cache(page, size, genre)

        if not films:
            start_index = (page - 1) * size
            if not genre:
                search_query = {
                    "query": {
                        "match_all": {}
                    },
                    "sort": [
                        {
                            "imdb_rating": {"order": "desc"}
                        }
                    ],
                    "from": start_index,
                    "size": size
                }
            else:
                search_query = {
                    "query": {
                        "nested": {
                            "path": "genre",
                            "query": {
                                "bool": {
                                    "filter": [
                                        {"term": {"genre.id": genre}}
                                    ]
                                }
                            }
                        }
                    },
                    "sort": [
                        {
                            "imdb_rating": {"order": "desc"}
                        }
                    ],
                    "from": start_index,
                    "size": size
                }

            total, films = await self._get_films_from_elastic(search_query)
            if not films:
                return 0, None
            await self._put_films_to_cache(page, size, total, films, genre)
            return total, films

        return total, films

    async def search_films(
        self,
        page: int,
        size: int,
        query: str
    ) -> tuple[int, list[FilmShort]]:
        """Retrieve films instances to list films
        in accordance with search conditions.

        """

        total, films = await self._films_from_cache(page, size, query)

        if not films:
            start_index = (page - 1) * size
            search_query = {
                "query": {
                    "match": {
                        "title": query
                    }
                },
                "sort": [
                    {
                        "_score": {"order": "desc"}
                    },
                    {
                        "imdb_rating": {"order": "desc"}
                    }
                ],
                "from": start_index,
                "size": size
            }

            total, films = await self._get_films_from_elastic(search_query)
            if not films:
                return 0, None
            await self._put_films_to_cache(page, size, total, films, query=query)
            return total, films
        return total, films

    async def _get_films_from_elastic(
        self,
        search_query: dict
    ) -> tuple[int, list[FilmShort]]:
        """Return a list of movies from Elasticsearch DB with a paginator.

        """

        result = await self.elastic.search(
            index=self.index_name,
            body=search_query
        )
        total = result['hits']['total']['value']
        hits = result['hits']['hits']

        if not hits:
            return total, []
        try:
            films = [hits[i]['_source'] for i in range(search_query['size'])]
        except IndexError:
            films = [hit['_source'] for hit in hits]

        return total, [FilmShort(**film) for film in films]

    async def get_by_id(self, film_id: str) -> FilmFull | None:
        """Return a film instance in accordance with ID given.

        """
        film = await self._film_from_cache(film_id)

        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> FilmFull | None:
        """Retrieve a film instance from Elasticsearch DB.

        """
        try:
            doc = await self.elastic.get(index=self.index_name, id=film_id)
        except NotFoundError:
            return None
        return FilmFull(**doc['_source'])

    async def _films_from_cache(
        self, page: int, size: int,
        query: str = None, genre: UUID = None
    ) -> tuple[int, list[FilmShort]]:
        """Retrieve films from Redis cache.

        """
        cache_key = f'films:{page}:{size}:{query}:{genre}'
        data = await self.redis.get(cache_key)
        if not data:
            return 0, None
        films_data = json.loads(data)
        films = [FilmShort.parse_raw(film) for film in films_data['films']]
        total = films_data['total']
        return total, films

    async def _film_from_cache(self, film_id: str) -> FilmFull | None:
        """Retrieve a film instance from Redis cache.

        """
        cache_key = f'film:{film_id}'
        data = await self.redis.get(cache_key)
        if not data:
            return None
        return FilmFull.parse_raw(data)

    async def _put_film_to_cache(self, film: FilmFull):
        """Save a film instance to Redis cache.

        """
        cache_key = f'film:{str(film.id)}'

        await self.redis.set(
            cache_key,
            film.json(),
            FILM_CACHE_EXPIRE_IN_SECONDS
        )

    async def _put_films_to_cache(
        self,
        page: int,
        size: int,
        total: int,
        films: list[FilmShort],
        query: str = None,
        genre: UUID = None
    ):
        """Save films to Redis cache.

        """
        cache_key = f'films:{page}:{size}:{query}:{genre}'
        data = {
            'total': total,
            'films': [film.json() for film in films]
        }
        json_str = json.dumps(data)
        await self.redis.set(cache_key, json_str, FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic, INDEX_NAME)
