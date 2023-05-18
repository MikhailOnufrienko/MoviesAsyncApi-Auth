import logging
from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import FilmPersonRoles, PersonShortFilmInfo
from models.person import PersonFull
from utils.search_films import get_films, get_roles

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


INDEX_NAME = 'person_index'


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

        person = await self._person_from_cache(person_id)

        if not person:
            person = await self._get_person_from_elastic(person_id)

            if not person:
                return None

            await self._put_person_to_cache(person)

        return person

    async def get_person_list(
        self, page: int, page_size: int, query: str | None
    ) -> tuple[int, list[PersonFull]]:
        """Returns a list of person data with filtering and sorting."""

        if query:
            query = {
                "match_phrase_prefix": {
                    "full_name": query
                }
            }
        else:
            query = {"match_all": {}}

        data = []
        from_page = (page - 1) * page_size

        try:
            response = await self.elastic.search(
                index=self.index_name, query=query, from_=from_page,
                size=page_size, sort=[{"id": {"order": "asc"}}]
            )
            total = response['hits']['total']['value']
            results = response['hits']['hits']
        except Exception as exc:
            logging.exception('An error occured: %s', exc)

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

    async def get_person_films_list(
        self, person_id: str
    ) -> tuple[int, list[PersonShortFilmInfo]]:
        """Data about films in which the person took part."""

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

        return len(films), films_data

    async def _get_person_from_elastic(
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

    async def _person_from_cache(self, person_id) -> PersonFull | None:
        """Request to Redis to get person data from the cache."""

        cache_key = f'person:{person_id}'
        data = await self.redis.get(cache_key)

        if not data:
            return None

        return PersonFull.parse_raw(data)

    async def _put_person_to_cache(self, person: PersonFull) -> None:
        """Put person data into the Redis cache."""

        cache_key = f'person:{str(person.id)}'

        await self.redis.set(
            cache_key,
            person.json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS,
        )


@lru_cache
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
    redis: Redis = Depends(get_redis)
) -> PersonService:
    return PersonService(elastic, redis, INDEX_NAME)
