import json
from uuid import UUID
from elasticsearch import NotFoundError
from db.elastic import AsyncSearchInterface
from db.redis import AsyncCacheInterface
from models.models import FilmFull, FilmShort


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 minutes


class ElasticService:
    def __init__(self, elastic: AsyncSearchInterface, index_name: str):
        self.elastic = elastic,
        self.index_name = index_name

    async def _get_film_from_elastic(self, film_id: str) -> FilmFull | None:
        """Retrieve a film instance from Elasticsearch DB.

        """
        try:
            doc = await self.elastic.get(index=self.index_name, id=film_id)
        except NotFoundError:
            return None
        return FilmFull(**doc['_source'])
    
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


class RedisService():
    def __init__(self, redis: AsyncCacheInterface):
        self.redis = redis

    async def _film_from_cache(self, film_id: str) -> FilmFull | None:
        """Retrieve a film instance from Redis cache.

        """
        cache_key = f'film:{film_id}'
        data = await self.redis.get(cache_key)
        if not data:
            return None
        return FilmFull.parse_raw(data)
    
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


redis_service = RedisService()
es_service = ElasticService()
