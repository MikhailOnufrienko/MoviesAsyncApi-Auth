import aiohttp
import pytest
from pytest_lazyfixture import lazy_fixture

from tests.functional.utils import es_queries, parametrize
from tests.functional.settings import test_settings
import redis.asyncio as redis
import json


@pytest.mark.parametrize(
    'person_id, expected_answer',
    parametrize.person_films_parameters
)
@pytest.mark.asyncio
async def test_person_film_list_response(
    es_write_data: callable,
    make_get_request: callable,
    person_id: str,
    expected_answer: dict
) -> None:
    """
    Sends a request to the person films API endpoint with a query by persom id
    and validates the given responses.
    """

    es_film_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_film_data, test_settings.es_movie_index)
    es_person_data = await es_queries.make_test_es_persons_data(
        existing_single_query=parametrize.PERSON_SINGLE_QUERY_EXIST,
        existing_multiple_query=parametrize.PERSON_MULTIPLE_QUERY_EXIST
    )
    await es_write_data(es_person_data, test_settings.es_person_index)

    url = test_settings.service_url + f'persons/{person_id}/film'
    response = await make_get_request(url)
    body, status = response.body, response.status

    assert status == expected_answer['status']

    if expected_answer['status'] == 200:
        assert body['total'] == 50
        assert len(body['results']) == 10


@pytest.mark.parametrize(
    'person_id, expected_answer,',
    parametrize.person_detail_parameters
)
@pytest.mark.asyncio
async def test_get_person_by_id(
    es_write_data: callable,
    make_get_request: callable,
    person_id: str,
    expected_answer: dict
) -> None:
    """
    Sends a request to the person detail API endpoint
    and validates the given responses.
    """

    es_film_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_film_data, test_settings.es_movie_index)
    es_person_data = await es_queries.make_test_es_persons_data(
        existing_single_query=parametrize.PERSON_SINGLE_QUERY_EXIST,
        existing_multiple_query=parametrize.PERSON_MULTIPLE_QUERY_EXIST
    )
    await es_write_data(es_person_data, test_settings.es_person_index)

    url = test_settings.service_url + f'persons/{person_id}'
    response = await make_get_request(url)
    body, status = response.body, response.status

    assert status == expected_answer['status']

    if expected_answer['status'] == 200:
        assert body['id'] == expected_answer['id']
        assert body['full_name'] == expected_answer['full_name']
        assert len(body['films']) == expected_answer['length']


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [parametrize.person_films_parameters[0]]
)
@pytest.mark.asyncio
async def test_person_film_list_redis_cache(
    redis_client: redis.Redis,
    es_write_data: callable,
    make_get_request: callable,
    person_id: str,
    expected_answer: dict
) -> None:
    """
    Sends a request to the person films API endpoint with a query by person id
    and verifies that the Redis cache is working properly.
    """

    # Check that current Redis cache is empty
    assert await redis_client.keys('*') == []

    es_film_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_film_data, test_settings.es_movie_index)
    es_person_data = await es_queries.make_test_es_persons_data(
        existing_single_query=parametrize.PERSON_SINGLE_QUERY_EXIST,
        existing_multiple_query=parametrize.PERSON_MULTIPLE_QUERY_EXIST
    )
    await es_write_data(es_person_data, test_settings.es_person_index)

    url = test_settings.service_url + f'persons/{person_id}/film'
    await make_get_request(url)

    assert len(await redis_client.keys('*')) == 1

    redis_key = f'person_films:{person_id}'
    data = await redis_client.get(redis_key)
    data = json.loads(data)

    assert data is not None
    assert data['total'] == expected_answer['length']
    assert len(data['person_films']) == expected_answer['body_length']


@pytest.mark.parametrize(
    'person_id, expected_answer',
    [parametrize.person_detail_parameters[0]]
)
@pytest.mark.asyncio
async def test_get_person_by_id_redis_cache(
    redis_client: redis.Redis,
    es_write_data: callable,
    make_get_request: callable,
    person_id: str,
    expected_answer: dict
) -> None:
    """
    Sends a request to the person detail API endpoint
    and verifies that the Redis cache is working properly.
    """

    # Check that current Redis cache is empty
    assert await redis_client.keys('*') == []

    es_film_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_film_data, test_settings.es_movie_index)
    es_person_data = await es_queries.make_test_es_persons_data(
        existing_single_query=parametrize.PERSON_SINGLE_QUERY_EXIST,
        existing_multiple_query=parametrize.PERSON_MULTIPLE_QUERY_EXIST
    )
    await es_write_data(es_person_data, test_settings.es_person_index)

    url = test_settings.service_url + f'persons/{person_id}'
    await make_get_request(url)

    assert len(await redis_client.keys('*')) == 1

    redis_key = f'person:{person_id}'
    data = await redis_client.get(redis_key)
    data = json.loads(data)

    assert data is not None
    assert data['id'] == expected_answer['id']
    assert data['full_name'] == expected_answer['full_name']
    assert len(data['films']) == expected_answer['length']
