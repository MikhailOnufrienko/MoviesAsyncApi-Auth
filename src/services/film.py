from functools import lru_cache
import json
from uuid import UUID

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

    async def get_films(self, page: int, size: int, genre: UUID) -> tuple[int, list[FilmShort]]:
        films = await self._films_from_cache(page, size, genre)
        if not films:

            start_index = (page - 1) * size
            
            if not genre:
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
                            "imdb_rating": {
                                "order": "desc"
                            }
                        }
                    ],
                    "from": start_index,
                    "size": size
                }

            total, films = await self._get_films_from_elastic(search_query)
            if not films:
                return None
            await self._put_films_to_cache(page, size, films, genre)
            return total, films
        total = len(films)
        return total, films

    async def search_films(self, query: str, page: int, size: int) -> tuple[int, list[FilmShort]]:
        
        films = await self._films_from_cache(query, page, size)
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
                        "_score": {
                            "order": "desc"
                        }
                    },
                    {
                        "imdb_rating": {
                            "order": "desc"
                        }
                    }
                ],
                "from": start_index,
                "size": size
            }

            total, films = await self._get_films_from_elastic(search_query)
            if not films:
                return None
            await self._put_films_to_cache(page, size, films, query=query)
            return total, films
        total = len(films)
        return total, films

    async def _get_films_from_elastic(self, search_query: dict) -> tuple[int, list[FilmShort]]:
        """Return a list of movies from Elasticsearch DB with a paginator."""

        result = await self.elastic.search(index='movies', body=search_query)
        total = result['hits']['total']['value']
        hits = result['hits']['hits']

        if not hits:
            return total, []
        try:
            films = [hits[i]['_source'] for i in range(search_query['size'])]
        except IndexError:
            films = [hit['_source'] for hit in hits]
            
        return total, [FilmShort(**film) for film in films]
    
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
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return FilmFull(**doc['_source'])

    async def _films_from_cache(self, page, size, query=None, genre=None):
        cache_key = f'films:{page}:{size}:{query}:{genre}'
        data = await self.redis.get(cache_key)
        if not data:
            return None
        films = [FilmShort.parse_raw(film) for film in data]
        return films

    async def _film_from_cache(self, film_id: str) -> FilmFull | None:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        cache_key = f'film:{film_id}'
        data = await self.redis.get(cache_key)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        return FilmFull.parse_raw(data)

    async def _put_film_to_cache(self, film: FilmFull):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        cache_key = f'film:{str(film.id)}'
        await self.redis.set(
            cache_key,
            film.json(),
            FILM_CACHE_EXPIRE_IN_SECONDS
            )
        
    async def _put_films_to_cache(self, page, size, films: list[FilmShort], query=None, genre=None):
        cache_key = f'films:{page}:{size}:{query}:{genre}'
        data = [film.json() for film in films]
        json_str = json.dumps(data)
        await self.redis.set(cache_key, json_str, FILM_CACHE_EXPIRE_IN_SECONDS)



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

