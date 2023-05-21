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
async def test_films_search_response(
    es_write_data: callable, make_get_request: callable,
    query_data: dict, expected_answer: dict
) -> None:
    """
    Sends a request to search for a movie on query
    and checks the response data.
    """

    es_data = await es_queries.make_test_es_movie_data(QUERY_EXIST)
    await es_write_data(es_data, test_settings.es_movie_index)

    url = test_settings.service_url + '/films/search'

    body, status = await make_get_request(url, query_data)

    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert (body['next'] is not None) == expected_answer['has_next_page']

    if expected_answer['has_next_page'] is True:
        url = test_settings.service_url + body['next']
        body, status = await make_get_request(url, query_data)

        assert body['prev'] is not None
        assert body['next'] is not None


@pytest.mark.asyncio
async def test_persons_search_response(
    make_get_request: callable,
    es_write_data: callable
):
    
    es_data = await es_queries.make_test_es_persons_data('Single Name')
    await es_write_data(es_data, 'person_index')

    url = test_settings.service_url + '/persons/search'

    query_data = {
        'query': 'Random Name',
        'page_number': 1,
        'page_size': 10 
    }

    body, status = await make_get_request(url, query_data)

    assert status == 200
    assert body['total'] == 21
    # assert body['total'] == 21
    # assert (body['next'] is not None) == True

    # assert True


@pytest.mark.asyncio
async def test_films_redis_cache(
    redis_client,
    make_get_request,
    es_write_data
):
    
    data = await redis_client.keys('*')
    assert data == []

    es_data = await es_queries.make_test_es_movie_data(QUERY_EXIST)
    await es_write_data(es_data, test_settings.es_movie_index)

    url = test_settings.service_url + '/films/search'
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
