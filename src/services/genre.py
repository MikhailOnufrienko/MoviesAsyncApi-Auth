import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import main as es_main
from db.redis import main as redis_main
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5

INDEX_NAME = 'genres'


class GenreService:

    def __init__(
        self, elastic: AsyncElasticsearch,
        redis: Redis, index_name: str
    ):
        """GenreService class initializing."""

        self.elastic = elastic
        self.redis = redis
        self.index_name = index_name

    async def get_by_id(self, genre_id: str) -> Genre | None:
        """Returns data about the genre by its id."""

        genre = await self._genre_from_cache(genre_id)

        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)

            if not genre:
                return None

            await self._put_genre_to_cache(genre)

        return genre

    async def get_genre_list(self, page: int, page_size: int) -> list[Genre]:
        """Returns a list of genre data."""

        query = {"match_all": {}}
        genre_data = []
        from_page = (page - 1) * page_size

        try:
            response = await self.elastic.search(
                index=self.index_name, from_=from_page,
                size=page_size, query=query
            )
            results = response['hits']['hits']

            for item in results:
                genre = item['_source']
                genre_data.append(
                    Genre(
                        id=genre['id'],
                        name=genre['name'],
                    )
                )

        except Exception as exc:
            logging.exception('An error occured: %s', exc)

        return genre_data

    async def _get_genre_from_elastic(self, genre_id: str) -> Genre | None:
        """Request to ElasticSearch to get genre data."""

        try:
            doc = await self.elastic.get(index=self.index_name, id=genre_id)
        except NotFoundError:
            return None

        return Genre(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> Genre | None:
        """Request to Redis to get genre data from the cache."""

        cache_key = f'genre:{genre_id}'
        data = await self.redis.get(cache_key)

        if not data:
            return None

        return Genre.parse_raw(data)

    async def _put_genre_to_cache(self, genre: Genre) -> None:
        """Put genre data into the Redis cache."""

        cache_key = f'genre:{str(genre.id)}'

        await self.redis.set(
            cache_key,
            genre.json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache
def get_genre_service(
    elastic: AsyncElasticsearch = Depends(es_main),
    redis: Redis = Depends(redis_main)
) -> GenreService:
    return GenreService(elastic, redis, INDEX_NAME)
