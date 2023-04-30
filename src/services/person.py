from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person


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
        
        return Person(**doc['_source'])


@lru_cache
def get_person_service(elastic = Depends(get_elastic)):
    return PersonService(elastic)
