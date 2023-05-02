from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from models.film import PersonShortFilm, PersonShortFilmInfo
import json
import logging
from utils.search_films import get_films, get_roles


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> tuple[Person | None, list]:
        """
        Returns information about the person by his id.

        Parameters:
            person_id: uuid of the person.

        Returns:
            person: person class object
            movie_data: list of films
        """

        try:
            doc = await self.elastic.get(
                index='person_index', id=person_id
            )
        except NotFoundError:
            return None

        person = doc['_source']
        films = await get_films(self.elastic, person['full_name'])
        movie_data = await get_roles(films, person['full_name'])
        person = Person(**person)

        return person, movie_data

    async def get_object_list(
        self, page: int,
        page_size: int, query: str | None
    ) -> list | None:
        """
        Returns a list with information about persons.

        Parameters:
            page: page number
            page_size: size of the page
            query: field that is searched for

        Returns:
            data: list of persons
        """

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
                index='person_index', query=query, from_=from_page,
                size=page_size, sort=[{"id": {"order": "asc"}}]
            )

            for person in response['hits']['hits']:
                person = person['_source']
                single_person_data = []
                single_person_data.append(Person(**person))

                films = await get_films(self.elastic, person['full_name'])
                movie_data = await get_roles(films, person['full_name'])

                single_person_data.append(movie_data)
                data.append(single_person_data)

        except Exception as exc:
            logging.exception('An error occured: %s', exc)

        return data

    async def get_films_by_person(self, person_id):
        """
        Get list of films where the person has participated.

        Parameters:
            person_id: uuid of the person

        Returns:
            movie_data: list of films
        """

        try:
            doc = await self.elastic.get(
                index='person_index', id=person_id
            )
        except NotFoundError:
            return None

        person = doc['_source']
        films = await get_films(self.elastic, person['full_name'])
        movie_data = []

        for film in films:

            obj = PersonShortFilmInfo(
                uuid=film['id'],
                title=film['title'],
                imdb_rating=film['imdb_rating']
            )
            movie_data.append(obj)

        return movie_data


@lru_cache
def get_person_service(elastic: AsyncElasticsearch = Depends(get_elastic)):
    return PersonService(elastic)
