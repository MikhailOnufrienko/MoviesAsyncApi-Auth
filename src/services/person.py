import json
import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic, AsyncSearchAbstract, elastic
from db.redis import get_redis, AsyncCacheAbstract, redis
from models.film import FilmPersonRoles, PersonShortFilmInfo
from models.person import PersonFull
from utils.search_films import get_films, get_roles


PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5

INDEX_NAME = 'person_index'


class ElasticService(AsyncSearchAbstract):
    def __init__(self, elastic: AsyncElasticsearch, index_name: str):
        self.elastic = elastic
        self.index_name = index_name

    async def _get_single_object(
        self, person_id: str
    ) -> PersonFull | None:
        """Request to ElasticSearch to get person data."""

        try:
            doc = await self.elastic.get(index=INDEX_NAME, id=person_id)
        except NotFoundError:
            return None

        person = doc['_source']
        films = await get_films(self.elastic, person['full_name'])
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
        self, query, page_size, from_page
    ) -> tuple[int, list[PersonFull]]:
        """Request to ElasticSearch to get a list of persons found
           in accordance with the query."""

        response = await self.elastic.search(
            index=self.index_name, query=query, from_=from_page,
            size=page_size, sort=[{"id": {"order": "asc"}}]
        )
        total = response['hits']['total']['value']
        results = response['hits']['hits']
        if not results:
            return total, []
        data = []
        for item in results:
            person = item['_source']
            films = await get_films(self.elastic, person['full_name'])
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
        self, page: int, size: int, query: str = None
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
        self, page: int, size: int, total: int,
        persons: list[PersonFull], query: str = None,
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
        self, person_id: str
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
        self, person_id: str, total: int, films: list[PersonShortFilmInfo]
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


es_service = ElasticService(elastic, INDEX_NAME)
redis_service = RedisService(redis)


class PersonService:
    def __init__(
        self, elastic: AsyncElasticsearch,
        redis: Redis, index_name: str
    ):
        """PersonService class initializing."""

        self.elastic = elastic
        self.redis = redis
        self.index_name = index_name

    async def get_by_id(self, person_id: str) -> PersonFull | None:
        """Returns data about the person by his id."""

        person = await redis_service._get_single_object(person_id)

        if not person:
            person = await es_service._get_single_object(person_id)

            if not person:
                return None

            await redis_service._put_single_object(person)

        return person

    async def get_person_list(
        self, page: int, page_size: int, search_query: str | None
    ) -> tuple[int, list[PersonFull]]:
        """Returns a list of person data with filtering and sorting."""

        total, data = await redis_service._get_list_of_objects(
            page, page_size, search_query
        )

        if not data:
            if search_query:
                query = {
                    "match_phrase_prefix": {
                        "full_name": search_query
                    }
                }
            else:
                query = {"match_all": {}}

            from_page = (page - 1) * page_size

            try:
                total, data = await es_service._get_list_of_objects(
                    query=query, page_size=page_size, from_page=from_page
                )
            except Exception as exc:
                logging.exception('An error occured: %s', exc)

            await redis_service._put_list_of_objects(
                page, page_size, total, data, search_query
            )
            return total, data
        return total, data

    async def get_person_films_list(
        self, person_id: str
    ) -> tuple[int, list[PersonShortFilmInfo]]:
        """Data about films in which the person took part."""

        total, films_data = await redis_service._person_films_from_cache(
            person_id
        )

        if not films_data:
            try:
                doc = await self.elastic.get(index=INDEX_NAME, id=person_id)
            except NotFoundError:
                return []

            person = doc['_source']
            films = await get_films(self.elastic, person['full_name'])
            films_data = []

            for film in films:
                obj = PersonShortFilmInfo(
                    id=film['id'],
                    title=film['title'],
                    imdb_rating=film['imdb_rating'],
                )
                films_data.append(obj)

            total = len(films_data)

            await redis_service._put_person_films_to_cache(
                person_id, total, films_data
            )
        return total, films_data


@lru_cache
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    redis: Redis = Depends(get_redis)
) -> PersonService:
    return PersonService(elastic, redis, INDEX_NAME)
