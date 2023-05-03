from elasticsearch import AsyncElasticsearch
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
                        "director": person_name
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

    films = await elastic.search(index="movies_index", query=query_movies)

    movie_data = [film['_source'] for film in films['hits']['hits']]

    return movie_data


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

        obj = FilmPersonRoles(uuid=film['id'], roles=roles)

        movie_data.append(obj)

    return movie_data
