import json

import pytest
import redis.asyncio as redis

from tests.functional.settings import test_settings
from tests.functional.utils import es_queries, parametrize


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
    Sends a request to the film API endpoint with a search query
    and validates the given responses.
    """

    es_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_data, test_settings.es_movie_index)

    url = test_settings.service_url + 'films/search'
    response = await make_get_request(url, query_data)
    body, status = response.body, response.status

    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert (body['next'] is not None) == expected_answer['has_next_page']

    if expected_answer['has_next_page'] is True:
        query_data = {
            'query': parametrize.FILM_QUERY_EXIST,
            'page_number': 2,
            'page_size': 10
        }
        response = await make_get_request(url, query_data)
        body, status = response.body, response.status

        assert body['prev'] is not None
        assert body['next'] is not None


@pytest.mark.parametrize(
    'query_data, expected_answer',
    parametrize.person_search_parameters
)
@pytest.mark.asyncio
async def test_persons_search_response(
    es_write_data: callable,
    make_get_request: callable,
    query_data: dict,
    expected_answer: dict
) -> None:
    """
    Sends a request to the person API endpoint with a search query
    and validates the given responses.
    """

    es_data = await es_queries.make_test_es_persons_data(
        existing_single_query=parametrize.PERSON_SINGLE_QUERY_EXIST,
        existing_multiple_query=parametrize.PERSON_MULTIPLE_QUERY_EXIST
    )
    await es_write_data(es_data, test_settings.es_person_index)

    url = test_settings.service_url + 'persons/search'
    response = await make_get_request(url, query_data)
    body, status = response.body, response.status

    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert (body['next'] is not None) == expected_answer['has_next_page']

    if expected_answer['has_next_page'] is True:

        query_data = {
            'query': parametrize.PERSON_SINGLE_QUERY_EXIST,
            'page_number': 2,
            'page_size': 10
        }
        response = await make_get_request(url, query_data)
        body, status = response.body, response.status

        assert body['prev'] is not None


@pytest.mark.asyncio
async def test_films_search_redis_cache(
    redis_client: redis.Redis,
    make_get_request: callable,
    es_write_data: callable
) -> None:
    """
    Sends a request to the film API endpoint with a search query
    and verifies that the Redis cache is working properly.
    """

    # Check that current Redis cache is empty
    assert await redis_client.keys('*') == []

    es_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_data, test_settings.es_movie_index)

    url = test_settings.service_url + 'films/search'
    query_data = {
        'query': parametrize.FILM_QUERY_EXIST,
        'page_number': 1,
        'page_size': 10
    }
    query, page, size = query_data.values()

    await make_get_request(url, query_data)

    redis_key = f'films:{page}:{size}:{query}:None'
    data = await redis_client.get(redis_key)
    data = json.loads(data)

    assert data is not None
    assert data['total'] == 50
    assert len(data['films']) == 10


@pytest.mark.parametrize(
    'query_data, expected_answer',
    parametrize.person_search_parameters
)
@pytest.mark.asyncio
async def test_persons_search_redis_cache(
    redis_client: redis.Redis,
    make_get_request: callable,
    es_write_data: callable,
    query_data, expected_answer
) -> None:
    """
    Sends a request to the person API endpoint with a search query
    and verifies that the Redis cache is working properly.
    """

    # Check that current Redis cache is empty
    assert await redis_client.keys('*') == []

    es_data = await es_queries.make_test_es_persons_data(
        existing_single_query=parametrize.PERSON_SINGLE_QUERY_EXIST,
        existing_multiple_query=parametrize.PERSON_MULTIPLE_QUERY_EXIST
    )
    await es_write_data(es_data, test_settings.es_person_index)

    url = test_settings.service_url + 'persons/search'
    # query_data = {
    #     'query': 'Name Name',
    #     'page_number': 1,
    #     'page_size': 10
    # }
    query, page, size = query_data.values()

    await make_get_request(url, query_data)

    redis_key = f'persons:{page}:{size}:{query}'
    data = await redis_client.get(redis_key)
    data = json.loads(data)

    assert data is not None
    assert data['total'] == expected_answer['length']
