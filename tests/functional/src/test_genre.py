import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings


async def test_genres():

    es_data = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Comedy',
            'description': 'Description of the genre "comedy".'
        } for _ in range(30)
    ]

    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {
                '_index': test_settings.es_genre_index, '_id': row[test_settings.es_id_field]
                }}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'

    es_client = AsyncElasticsearch(hosts=test_settings.es_host, 
                                   validate_cert=False, 
                                   use_ssl=False)
    response = await es_client.bulk(str_query, refresh=True)
    await es_client.close()
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')
    
    session = aiohttp.ClientSession()
    url = test_settings.service_url + 'genres'

    async with session.get(url) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
    await session.close()

    assert status == 200
    assert len(response.body) == 30
    