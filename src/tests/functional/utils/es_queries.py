import json
import uuid


async def make_test_es_movie_data(
    existing_film_query: str,
    existing_person_query: str
) -> list:
    """Create test data for ElasticSearch."""

    film_ids = [
        'b8076788-de5b-426a-b78b-08e9dc819841'
    ] + [str(uuid.uuid4()) for _ in range(49)]

    return [{
        'id': film_ids[i],
        'imdb_rating': 8.5,
        'genres': [
            {
                'id': '120a21cf-9097-479e-904a-13dd7198c1dd',
                'name': 'Adventure',
                'description': 'Exciting and unusual experience.',
            }
        ],
        'title': existing_film_query,
        'description': 'New World',
        'directors': [
            {
                'id': 'a0077238-c960-4c22-9824-e49d8585cf3d',
                'name': 'Main Director'
            }
        ],
        'actors_names': [existing_person_query, 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {
                'id': '32b50c6b-4907-292f-b652-6ef2ee8b43f8',
                'name': existing_person_query
            },
            {
                'id': '222',
                'name': 'Bob'
            }
        ],
        'writers': [
            {
                'id': '333',
                'name': 'Ben'
            },
            {
                'id': '444',
                'name': 'Howard'
            }
        ],
    } for i in range(50)]


async def make_test_es_persons_data(
    existing_single_query: str, existing_multiple_query: str
) -> list:
    """Create test data for ElasticSearch."""

    return [{
        'id': str(uuid.uuid4()),
        'full_name': existing_multiple_query,
    } for _ in range(20)] + [{
        'id': '32b50c6b-4907-292f-b652-6ef2ee8b43f8',
        'full_name': existing_single_query,
    }]


async def make_test_es_genres_data():
    """Generate test genre data."""

    return [{
        'id': str(uuid.uuid4()),
        'name': 'Comedy',
        'description': 'Movies to make you laugh:)'
    } for _ in range(9)] + [{
        'id': '120a21cf-9097-479e-904a-13dd7198c1dd',
        'name': 'Adventure',
        'description': 'Exciting and unusual experience.'
    }]


async def get_es_bulk_query(data: list, index: str, id_field: str) -> list:
    """Creates a list with es_data in json format."""

    bulk_query = []

    for row in data:
        bulk_query.extend([
            json.dumps(
                {
                    'index': {
                        '_index': index,
                        '_id': row[id_field],
                    }
                }
            ),
            json.dumps(row)
        ])

    return bulk_query
