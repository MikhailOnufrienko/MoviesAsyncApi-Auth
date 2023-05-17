import pytest

from tests.functional.settings import test_settings
from tests.functional.utils import es_queries
from tests.functional.utils import parametrize
import json

import redis.asyncio as redis


r = redis.Redis()

QUERY_EXIST = 'PYTESTFILMS'
QUERY_NOT_EXIST = 'NOTEXIST'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    parametrize.film_search_parameters
)
@pytest.mark.asyncio
async def test_search(
    es_write_data: callable,
    make_get_request: callable,
    redis_cleare_cache: callable,
    query_data: dict,
    expected_answer: dict
):

    es_data = await es_queries.make_test_es_data(QUERY_EXIST)
    await es_write_data(es_data)

    url = test_settings.base_url + '/films/search'

    body, status = await make_get_request(url, query_data)

    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert (body['next'] is not None) == expected_answer['has_next_page']

    if expected_answer['has_next_page'] is True:
        url = test_settings.base_url + body['next']
        page2_query = {
            'query': QUERY_EXIST,
            'page_size': 10
        }
        body, status = await make_get_request(url, page2_query)

        assert body['prev'] is not None
        assert body['next'] is not None




@pytest.mark.asyncio
async def test_redis_films_cache(
    redis_client,
    make_get_request,
    es_write_data
):
    
    data = await redis_client.keys('*')
    assert data == []

    es_data = await es_queries.make_test_es_data(QUERY_EXIST)
    await es_write_data(es_data)

    url = test_settings.base_url + '/films/search'
    query_data = {
        'query': QUERY_EXIST,
        'page_number': 1,
        'page_size': 10
    }
    query, page, size = query_data.values()

    await make_get_request(url, query_data)

    redis_key = f"films:{page}:{size}:{query}:None"
    data = await redis_client.get(redis_key)
    data = json.loads(data)

    assert data is not None
    assert data['total'] == 50
    assert len(data['films']) == 10
