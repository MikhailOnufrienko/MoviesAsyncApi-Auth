from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


# class GenreServise:

#     def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
#         self.redis = redis
#         self.elastic = elastic
    
#     async def get_by_id(self, genre_id: str) -> Genre | None:
#         """Get genre object by id, if not exists, return None."""

#         genre = await self._genre_from_cache(genre_id)

#         if not genre:
#             genre = await self._get_genre_from_elastic(genre_id)

#             if not genre:
#                 return None
        
#             await self._put_genre_to_cache(genre)
        
#         return genre
    
#     async def _get_genre_from_elastic(self, genre_id: str) -> Genre | None:
#         """Get genre from elastic by id, if not found, return None."""

#         try:
#             doc = await self.elastic.get('genres', genre_id)
#         except NotFoundError:
#             return None
        
#         return Genre(**doc['_source'])
    
#     async def _genre_from_cache(self, genre_id: str) -> Genre | None:
#         """Trying to get genre from Redis cache, if not, return None."""

#         data = await self.redis.get(genre_id)

#         if not data:
#             return None
    
#         genre = Genre.parse_raw(data)
#         return genre

#     async def _put_genre_to_cache(self, genre: Genre) -> None:
#         """Put Genre object to Redis cache."""

#         await self.redis.set(
#             name=genre.id,
#             value=genre.json(),
#             ex=GENRE_CACHE_EXPIRE_IN_SECONDS
#         )


# @lru_cache()
# def get_genre_service(
#     redis: Redis = Depends(get_redis),
#     elastic: AsyncElasticsearch = Depends(get_elastic),
# ) -> GenreServise:
#     return GenreServise(redis, elastic)


class GenreServise:

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic
    
    async def get_by_id(self, genre_id: str) -> Genre | None:
        """Get genre object by id, if not exists, return None."""

        genre = await self._get_genre_from_elastic(genre_id)

        if not genre:
            return None
        
        return genre
    
    async def _get_genre_from_elastic(self, genre_id: str) -> Genre | None:
        """Get genre from elastic by id, if not found, return None."""

        try:
            doc = await self.elastic.get(
                index='person_index', id=genre_id
            )
        except NotFoundError:
            return None
        
        return Genre(**doc['_source'])

    # async def _genre_from_cache(self, genre_id: str) -> Genre | None:
    #     """Trying to get genre from Redis cache, if not, return None."""

    #     data = await self.redis.get(genre_id)

    #     if not data:
    #         return None
    
    #     genre = Genre.parse_raw(data)
    #     return genre

    # async def _put_genre_to_cache(self, genre: Genre) -> None:
    #     """Put Genre object to Redis cache."""

    #     await self.redis.set(
    #         name=genre.id,
    #         value=genre.json(),
    #         ex=GENRE_CACHE_EXPIRE_IN_SECONDS
    #     )


@lru_cache
def get_genre_service(
    elastic = Depends(get_elastic)
):
    return GenreServise(elastic)
