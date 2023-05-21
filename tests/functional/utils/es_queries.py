import uuid
import json
import names


async def make_test_es_movie_data(existing_query: str) -> list:
    """Create test data for ElasticSearch."""

    return [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': [
            {
                'id': str(uuid.uuid4()),
                'name': 'Genre',
                'description': 'Empty',
            } for _ in range(2)
        ],
        'title': existing_query,
        'description': 'New World',
        'director': [
            {
                'id': str(uuid.uuid4()),
                'name': 'Main Director'
            }
        ],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
    } for _ in range(50)]


async def make_test_es_persons_data(existing_query: str) -> list:
    """Create test data for ElasticSearch."""

    data = [{
        'id': str(uuid.uuid4()),
        'full_name': 'Random Name',
    } for _ in range(20)] + [{
        'id': str(uuid.uuid4()),
        'full_name': existing_query,
    }]
    
    # data.append({
    #     'id': str(uuid.uuid4()),
    #     'full_name': existing_query,
    # })

    return data


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
