import json
import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from core.config import settings
from db.elastic import AsyncSearchAbstract, elastic, get_elastic
from db.redis import AsyncCacheAbstract, get_redis, redis
from models.film import FilmPersonRoles, PersonShortFilmInfo
from models.person import PersonFull
from redis.asyncio import Redis
from utils.search_films import get_films, get_roles

PERSON_CACHE_EXPIRE_IN_SECONDS = settings.REDIS_CACHE_EXPIRES_IN_SECONDS
INDEX_NAME = settings.ES_PERSON_INDEX


class ElasticService(AsyncSearchAbstract):
    """Class to represent search engine with ElasticSearch."""

    def __init__(self, elastic: AsyncElasticsearch, index_name: str):
        self.elastic = elastic
        self.index_name = index_name

    async def _get_single_object(self, person_id: str) -> PersonFull | None:
        """Request to ElasticSearch to get person data."""

        try:
            doc = await self.elastic.get(index=INDEX_NAME, id=person_id)
        except NotFoundError:
            return None

        person = doc['_source']
        _, films = await get_films(self.elastic, person['full_name'])
        films_roles = await get_roles(films, person['full_name'])

        return PersonFull(
            id=person['id'],
            full_name=person['full_name'],
            films=[
                FilmPersonRoles(
                    id=film.id,
                    roles=film.roles,
                ) for film in films_roles
            ]
        )

    async def _get_list_of_objects(
        self,
        query: str,
        page_size: int,
        from_page: int
    ) -> tuple[int, list[PersonFull]]:
        """
        Request to ElasticSearch to get a list of persons found
        in accordance with the query.
        """

        response = await self.elastic.search(
            index=self.index_name, query=query, from_=from_page,
            size=page_size
        )
        total = response['hits']['total']['value']
        results = response['hits']['hits']

        if not results:
            return total, []

        data = []

        for item in results:
            person = item['_source']
            _, films = await get_films(self.elastic, person['full_name'])
            films_roles = await get_roles(films, person['full_name'])
            data.append(
                PersonFull(
                    id=person['id'],
                    full_name=person['full_name'],
                    films=[
                        FilmPersonRoles(
                            id=film.id,
                            roles=film.roles,
                        ) for film in films_roles
                    ]
                )
            )

        return total, data


class RedisService(AsyncCacheAbstract):
    """Class to represent cache service with Redis."""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def _get_single_object(self, person_id) -> PersonFull | None:
        """Request to Redis to get person data from the cache."""

        cache_key = f'person:{person_id}'
        data = await self.redis.get(cache_key)

        if not data:
            return None

        return PersonFull.parse_raw(data)

    async def _get_list_of_objects(
        self,
        page: int,
        size: int,
        query: str = None
    ) -> tuple[int, list[PersonFull]]:
        """Get person list data from Redis cache."""

        cache_key = f'persons:{page}:{size}:{query}'
        data = await self.redis.get(cache_key)

        if not data:
            return 0, []

        persons_data = json.loads(data)
        persons = [
            PersonFull.parse_raw(person) for person in persons_data['persons']
        ]
        total = persons_data['total']

        return total, persons

    async def _put_single_object(self, person: PersonFull) -> None:
        """Put person data into the Redis cache."""

        cache_key = f'person:{str(person.id)}'

        await self.redis.set(
            cache_key,
            person.json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS,
        )

    async def _put_list_of_objects(
        self,
        page: int,
        size: int,
        total: int,
        persons: list[PersonFull],
        query: str = None,
    ) -> None:
        """Put person list data into Redis cache."""

        cache_key = f'persons:{page}:{size}:{query}'
        data = {
            'total': total,
            'persons': [person.json() for person in persons]
        }
        json_str = json.dumps(data)

        await self.redis.set(
            cache_key,
            json_str,
            PERSON_CACHE_EXPIRE_IN_SECONDS
        )

    async def _person_films_from_cache(
        self,
        person_id: str
    ) -> tuple[int, list[PersonShortFilmInfo]]:
        """Get person film list data from Redis cache."""

        cache_key = f'person_films:{person_id}'
        data = await self.redis.get(cache_key)

        if not data:
            return 0, []

        films_data = json.loads(data)
        films = [
            PersonShortFilmInfo.parse_raw(film)
            for film in films_data['person_films']
        ]
        total = films_data['total']

        return total, films

    async def _put_person_films_to_cache(
        self,
        person_id: str,
        total: int,
        films: list[PersonShortFilmInfo]
    ) -> None:
        """Put person film list data into Redis cache."""

        cache_key = f'person_films:{person_id}'
        data = {
            'total': total,
            'person_films': [film.json() for film in films]
        }
        json_str = json.dumps(data)

        await self.redis.set(
            cache_key,
            json_str,
            PERSON_CACHE_EXPIRE_IN_SECONDS
        )


search_service = ElasticService(elastic, INDEX_NAME)
cache_service = RedisService(redis)


class PersonService:
    """Class to represent persons logic."""

    def __init__(
        self,
        elastic: AsyncElasticsearch,
        redis: Redis,
        index_name: str
    ) -> None:
        self.elastic = elastic
        self.redis = redis
        self.index_name = index_name

    async def get_by_id(self, person_id: str) -> PersonFull | None:
        """Returns data about the person by his id."""

        person = await cache_service._get_single_object(person_id)

        if not person:
            person = await search_service._get_single_object(person_id)

            if not person:
                return None

            await cache_service._put_single_object(person)

        return person

    async def get_person_list(
        self,
        page: int,
        page_size: int,
        search_query: str | None
    ) -> tuple[int, list[PersonFull]]:
        """Returns a list of person data with filtering and sorting."""

        total, data = await cache_service._get_list_of_objects(
            page, page_size, search_query
        )

        if not data:
            if search_query:
                query = {
                    "match_phrase_prefix": {"full_name": search_query}
                }
            else:
                query = {"match_all": {}}

            from_page = (page - 1) * page_size

            try:
                total, data = await search_service._get_list_of_objects(
                    query=query, page_size=page_size, from_page=from_page
                )
            except Exception as exc:
                logging.exception('An error occured: %s', exc)

            await cache_service._put_list_of_objects(
                page, page_size, total, data, search_query
            )

            return total, data

        return total, data

    async def get_person_films_list(
        self,
        person_id: str
    ) -> tuple[int, list[PersonShortFilmInfo]]:
        """Data about films in which the person took part."""

        total, films_data = await cache_service._person_films_from_cache(
            person_id
        )

        if not films_data:
            try:
                doc = await self.elastic.get(index=INDEX_NAME, id=person_id)
            except NotFoundError:
                return 0, []

            person = doc['_source']
            total, films = await get_films(self.elastic, person['full_name'])
            films_data = []

            for film in films:
                obj = PersonShortFilmInfo(
                    id=film['id'],
                    title=film['title'],
                    imdb_rating=film['imdb_rating'],
                )
                films_data.append(obj)

            await cache_service._put_person_films_to_cache(
                person_id, total, films_data
            )

        return total, films_data


@lru_cache
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    redis: Redis = Depends(get_redis)
) -> PersonService:
    return PersonService(elastic, redis, INDEX_NAME)
