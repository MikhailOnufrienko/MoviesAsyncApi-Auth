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
from utils.search_films import get_films


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
    
        person = doc['_source']
        movies_data = await get_films(self.elastic, person['full_name'])

        return Person(**person), movies_data

    async def get_object_list(self, page, page_size, query) -> list | None:

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
            hits = response['hits']['hits']

            for person in hits:
                person = person['_source']
                single_person_data = []
                single_person_data.append(Person(**person))

                movie_data = await get_films(self.elastic, person['full_name'])

                single_person_data.append(movie_data)

                data.append(single_person_data)

                # query_movies = {
                #     "bool": {
                #         "should": [
                #             { "match_phrase": { "actors_names": person_name } },
                #             { "match_phrase": { "director": person_name } },
                #             { "match_phrase": { "writers_names": person_name } }
                #         ]
                #     }
                # }

                # results = await self.elastic.search(index="movies_index", query=query_movies)

                # movie_data = []

                # for movie in results['hits']['hits']:
                #     movie = movie['_source']
                #     roles = []
                    # if movie['actors_names'] is not None and person_name in movie['actors_names']:
                    #     roles.append('actor')
                    # if movie['director'] is not None and person_name in movie['director']:
                    #     roles.append('director')
                    # if movie['writers_names'] is not None and person_name in movie['writers_names']:
                    #     roles.append('writer')
                #     obj = PersonShortFilm(uuid=movie['id'], roles=roles)
                #     movie_data.append(obj)
                
                # single_person_data.append(movie_data)

                # data.append(single_person_data)



        except Exception as exc:
            logging.exception('An error occured: %s', exc)

        return data


@lru_cache
def get_person_service(elastic = Depends(get_elastic)):
    return PersonService(elastic)
