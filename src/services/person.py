from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from models.film import PersonShortFilm
import json
import logging


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic
    
    async def get_by_id(self, person_id: str) -> Person | None:
        
        try:
            doc = await self.elastic.get(
                index='person_index', id=person_id
            )
        except NotFoundError:
            return None
    
        person_name = doc['_source']['full_name']

        query_movies = {
            "bool": {
                "should": [
                    { "match_phrase": { "actors_names": person_name } },
                    { "match_phrase": { "director": person_name } },
                    { "match_phrase": { "writers_names": person_name } }
                ]
            }
        }

        results = await self.elastic.search(index="movies_index", query=query_movies)

        movie_data = []

        for movie in results['hits']['hits']:
            movie = movie['_source']
            roles = []
            if person_name in movie['actors_names']:
                roles.append('actor')
            if person_name in movie['director']:
                roles.append('director')
            if person_name in movie['writers_names']:
                roles.append('writer')
            obj = PersonShortFilm(uuid=movie['id'], roles=roles)
            movie_data.append(obj)

        return Person(**doc['_source']), movie_data

        # query_movies = {
        #     "bool": {
        #         "should": [
        #             { "match": { "actors_names": person_name } },
        #             { "match": { "director": person_name } },
        #             { "match": { "writers_names": person_name } }
        #         ]
        #     }
        # }

        # results = self.elastic.search(index="movies_index", query=query_movies)

        # print(results['hits']['hits'])

        # counter += 1

        # return Person(**doc['_source'])

    async def get_object_list(self, page, page_size, query) -> list | None:

        if query:
            query = {
                "match_phrase_prefix": {
                    "full_name": query
                }
            }
        else:
            query = {"match_all": {}}

        person_data = []

        from_page = (page - 1) * page_size

        try:
            response = await self.elastic.search(
                index='person_index', query=query, from_=from_page,
                size=page_size, sort=[{"id": {"order": "asc"}}]
            )
            hits = response['hits']['hits']

            counter = 0

            for person in hits:
                person_data.append(Person(**person['_source']))






        except Exception as exc:
            logging.exception('An error occured: %s', exc)

        return person_data


@lru_cache
def get_person_service(elastic = Depends(get_elastic)):
    return PersonService(elastic)
