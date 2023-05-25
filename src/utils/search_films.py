from elasticsearch import AsyncElasticsearch

from core.config import settings
from models.film import FilmPersonRoles


async def get_films(elastic: AsyncElasticsearch, person_name: str) -> list:
    """Returns the list of movies in which the person participated."""

    query_movies = {
        "bool": {
            "should": [
                {
                    "match_phrase": {
                        "actors_names": person_name
                    }
                },
                {
                    "match_phrase": {
                        "directors": person_name
                    }
                },
                {
                    "match_phrase": {
                        "writers_names": person_name
                    }
                },
            ]
        }
    }

    films = await elastic.search(
        index=settings.ES_MOVIE_INDEX,
        query=query_movies
    )

    try:
        total = films['hits']['total']['value']
    except Exception:
        total = 0

    movie_data = [film['_source'] for film in films['hits']['hits']]

    return total, movie_data


async def get_roles(films: list, person_name: str) -> list:
    """"""

    ROLES_DATA = {
        'actors_names': 'actor',
        'director': 'director',
        'writers_names': 'writer',
    }

    movie_data = []

    for film in films:
        roles = []

        for field, role in ROLES_DATA.items():
            try:
                roles.append(role) if person_name in film[field] else None
            except Exception:
                pass

        obj = FilmPersonRoles(id=film['id'], roles=roles)

        movie_data.append(obj)

    return movie_data
