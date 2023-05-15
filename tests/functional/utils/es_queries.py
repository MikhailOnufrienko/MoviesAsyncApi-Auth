import uuid
import json

from tests.functional.settings import test_settings


async def make_test_es_data(existing_query):
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


async def get_es_bulk_query(data, index_name, id_field):
    bulk_query = []
    
    for row in data:
        bulk_query.extend([
            json.dumps(
                {
                    'index': {
                        '_index': index_name,
                        '_id': row[str(id_field)],
                    }
                }
            ),
            json.dumps(row)
        ])

    return bulk_query
