from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch.helpers import async_scan
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.models import FilmFull, FilmShort


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


# FilmService содержит бизнес-логику по работе с фильмами. 
# Никакой магии тут нет. Обычный класс с обычными методами. 
# Этот класс ничего не знает про DI — максимально сильный и независимый.
class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_films(self, skip: int = 0, limit: int = 50) -> list[FilmShort]:
        search_query = {
            "query": {
                "match_all": {}
            },
            "sort": [
                {
                    "imdb_rating": {
                        "order": "desc"
                    }
                }
            ],
            "from": skip,
            "size": limit
        }

        films = await self._get_films_from_elastic(search_query)
        return films

    async def _get_films_from_elastic(self, search_query: str) -> list[FilmShort]:
        """Return a list of movies."""

#        async with self.elastic as es_client:
#            async for doc in es_client.search(index='movies', body=search_query):
#                yield doc["_source"]

#        for doc in async_scan(self.elastic, query=search_query, index='movies'):
#            return doc["_source"]
        result = await self.elastic.search(index='movies', body=search_query)
        hits = result['hits']['hits']
        films = [hits[i]['_source'] for i in range(search_query['size'])]
            
        return [FilmShort(**film) for film in films]
    
    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> FilmFull | None:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> FilmFull | None:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return FilmFull(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> FilmFull | None:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = FilmFull.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: FilmFull):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)



# get_film_service — это провайдер FilmService. 
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Для их получения вы ранее создали функции-провайдеры в модуле db
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)

