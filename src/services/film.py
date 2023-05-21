from functools import lru_cache
from uuid import UUID

from fastapi import Depends

from db.elastic import AsyncSearchInterface, main as es_main
from db.redis import AsyncCacheInterface, main as redis_main
from models.models import FilmFull, FilmShort
from services.services import es_service, redis_service


INDEX_NAME = 'movies'


class FilmService:
    """Class to represent films logic."""

    async def get_films(
            self,
            page: int,
            size: int,
            genre: UUID
    ) -> tuple[int, list[FilmShort]]:
        """Retrieve films instances to list films
        in accordance with filtration conditions.

        """
        total, films = await redis_service._films_from_cache(page, size, genre)

        if not films:
            start_index = (page - 1) * size
            if not genre:
                search_query = {
                    "query": {
                        "match_all": {}
                    },
                    "sort": [
                        {
                            "imdb_rating": {"order": "desc"}
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
                            "imdb_rating": {"order": "desc"}
                        }
                    ],
                    "from": start_index,
                    "size": size
                }
            
            total, films = await es_service._get_films_from_elastic(search_query)
            if not films:
                return 0, None
            await redis_service._put_films_to_cache(page, size, total, films, genre)
            return total, films
        return total, films

    async def search_films(
        self,
        page: int,
        size: int,
        query: str
    ) -> tuple[int, list[FilmShort]]:
        """Retrieve films instances to list films
        in accordance with search conditions.

        """

        total, films = await redis_service._films_from_cache(page, size, query)

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
                        "_score": {"order": "desc"}
                    },
                    {
                        "imdb_rating": {"order": "desc"}
                    }
                ],
                "from": start_index,
                "size": size
            }
            
            total, films = await es_service._get_films_from_elastic(search_query)
            if not films:
                return 0, None
            await redis_service._put_films_to_cache(page, size, total, films, query)
            return total, films
        return total, films

    async def get_by_id(self, film_id: str) -> FilmFull | None:
        """Return a film instance in accordance with ID given.

        """
        film = await redis_service._film_from_cache(film_id)

        if not film:
            film = await es_service._get_film_from_elastic(film_id)
            if not film:
                return None
            await redis_service._put_film_to_cache(film)
        return film


@lru_cache()
def get_film_service(
        redis: AsyncCacheInterface = Depends(redis_main),
        elastic: AsyncSearchInterface = Depends(es_main),
) -> FilmService:
    return FilmService(redis, elastic, INDEX_NAME)
