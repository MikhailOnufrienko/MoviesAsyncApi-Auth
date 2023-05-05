from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
import logging


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5

INDEX_NAME = 'genre_index'


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

    async def get_genre_list(self) -> list[Genre]:
        """Returns a list of genre data."""

        query = {"match_all": {}}
        genre_data = []

        try:
            response = await self.elastic.search(
                index=self.index_name,
                query=query,
            )
            results = response['hits']['hits']
            genre_data.append(Genre(**genre['_source']) for genre in results)
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

        data = await self.redis.get(genre_id)

        if not data:
            return None

        return Genre.parse_raw(data)

    async def _put_genre_to_cache(self, genre: Genre) -> None:
        """Putting genre data into the Redis cache."""

        await self.redis.set(
            str(genre.id),
            genre.json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache
def get_genre_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    redis: Redis = Depends(get_redis),
) -> GenreService:
    return GenreService(elastic, redis, INDEX_NAME)
