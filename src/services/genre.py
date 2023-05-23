import json
# import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from db.elastic import AsyncSearchAbstract, get_elastic, elastic
from db.redis import AsyncCacheAbstract, get_redis, redis

from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5

INDEX_NAME = 'genres'


class ElasticService(AsyncSearchAbstract):
    def __init__(self, elastic: AsyncElasticsearch, index_name: str):
        self.elastic = elastic
        self.index_name = index_name

    async def _get_single_object(self, genre_id: str) -> Genre | None:
        """Request to ElasticSearch to get genre data."""

        try:
            doc = await self.elastic.get(index=self.index_name, id=genre_id)
        except NotFoundError:
            return None

        return Genre(**doc['_source'])

    async def _get_list_of_objects(
            self,
            search_query: dict
    ) -> tuple[int, list[Genre]]:
        """Request to ElasticSearch to get a list of genres
        and total number of genres."""

        result = await self.elastic.search(
            index=self.index_name,
            body=search_query
        )
        total = result['hits']['total']['value']
        hits = result['hits']['hits']

        if not hits:
            return total, []
        try:
            genres = [hits[i]['_source'] for i in range(search_query['size'])]
        except IndexError:
            genres = [hit['_source'] for hit in hits]

        return total, [Genre(**genre) for genre in genres]


class RedisService(AsyncCacheAbstract):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def _get_single_object(self, genre_id: str) -> Genre | None:
        """Request to Redis to get genre data from the cache."""

        cache_key = f'genre:{genre_id}'
        data = await self.redis.get(cache_key)

        if not data:
            return None

        return Genre.parse_raw(data)

    async def _get_list_of_objects(
            self, page: int, page_size: int
    ) -> tuple[int, list[Genre]]:
        """Retrieve genres from Redis cache.

        """
        cache_key = f'genres:{page}:{page_size}'
        data = await self.redis.get(cache_key)

        if not data:
            return 0, None
        genres_data = json.loads(data)
        films = [Genre.parse_raw(genre) for genre in genres_data['genres']]
        total = genres_data['total']

        return total, films

    async def _put_single_object(self, genre: Genre) -> None:
        """Put genre data into the Redis cache."""

        cache_key = f'genre:{str(genre.id)}'

        await self.redis.set(
            cache_key,
            genre.json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS,
        )

    async def _put_list_of_objects(
        self,
        page: int,
        page_size: int,
        total: int,
        genres: list[Genre]
    ):
        """Save genres to Redis cache.

        """
        cache_key = f'genres:{page}:{page_size}'
        data = {
            'total': total,
            'genres': [genre.json() for genre in genres]
        }
        json_str = json.dumps(data)
        await self.redis.set(cache_key, json_str,
                             GENRE_CACHE_EXPIRE_IN_SECONDS)


redis_service = RedisService(redis)
es_service = ElasticService(elastic, INDEX_NAME)


class GenreService:

    def __init__(
        self, elastic: AsyncSearchAbstract,
        redis: AsyncCacheAbstract, index_name: str
    ):
        """GenreService class initializing."""

        self.elastic = elastic
        self.redis = redis
        self.index_name = index_name

    async def get_by_id(self, genre_id: str) -> Genre | None:
        """Returns data about the genre by its id."""

        genre = await redis_service._get_single_object(genre_id)

        if not genre:
            genre = await es_service._get_single_object(genre_id)

            if not genre:
                return None

            await redis_service._put_single_object(genre)

        return genre

    async def get_genre_list(
            self, page: int, page_size: int
    ) -> tuple[int, list[Genre]]:
        """Returns a list of genre data."""

        total, genre_data = await redis_service._get_list_of_objects(
            page, page_size
        )
        if not genre_data:
            start_index = (page - 1) * page_size
            query = {
                "query": {
                    "match_all": {}
                },
                "from": start_index,
                "size": page_size
            }
            total, genre_data = await es_service._get_list_of_objects(query)
            if not genre_data:
                return 0, None
            await redis_service._put_list_of_objects(page, page_size,
                                                     total, genre_data)
            return total, genre_data
#           except Exception as exc:
#              logging.exception('An error occured: %s', exc)
        return total, genre_data


@lru_cache
def get_genre_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    redis: Redis = Depends(get_redis)
) -> GenreService:
    return GenreService(elastic, redis, INDEX_NAME)
