from elasticsearch import AsyncElasticsearch
from models.film import PersonShortFilm


async def get_films(elastic: AsyncElasticsearch, person_name: str) -> list:
    """Returns list of films that person has participated."""

    query_movies = {
        "bool": {
            "should": [
                { "match_phrase": { "actors_names": person_name } },
                { "match_phrase": { "director": person_name } },
                { "match_phrase": { "writers_names": person_name } }
            ]
        }
    }

    films = await elastic.search(index="movies_index", query=query_movies)

    movie_data = []

    for film in films['hits']['hits']:
        film = film['_source']
        roles = []

        if film['actors_names'] is not None and person_name in film['actors_names']:
            roles.append('actor')
        if film['director'] is not None and person_name in film['director']:
            roles.append('director')
        if film['writers_names'] is not None and person_name in film['writers_names']:
            roles.append('writer')
        
        obj = PersonShortFilm(uuid=film['id'], roles=roles)
        movie_data.append(obj)
    
    return movie_data
        


