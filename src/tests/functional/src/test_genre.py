import json
from http import HTTPStatus

import pytest

from tests.functional.settings import test_settings
from tests.functional.utils import es_queries, parametrize


@pytest.mark.asyncio
async def test_get_all_genres(
    es_write_data: callable,
    make_get_request: callable
) -> None:
    """
    Sends a request to the genre API endpoint
    and validates the given responses.
    """

    es_data = await es_queries.make_test_es_genres_data()
    await es_write_data(es_data, test_settings.es_genre_index)

    url = test_settings.service_url + 'genres/'
    response = await make_get_request(url)
    body, status = response.body, response.status

    assert status == HTTPStatus.OK
    assert len(body['results']) == 10


@pytest.mark.parametrize(
    'genre_id, expected_answer',
    parametrize.genre_detail_parameters
)
@pytest.mark.asyncio
async def test_get_genre_by_id(
    es_write_data: callable,
    make_get_request: callable,
    genre_id: str,
    expected_answer: dict
):
    """
    Sends a request to the genre detail API endpoint
    and validates the given responses.
    """

    es_data = await es_queries.make_test_es_genres_data()
    await es_write_data(es_data, test_settings.es_genre_index)

    url = test_settings.service_url + f'genres/{genre_id}'
    response = await make_get_request(url)
    body, status = response.body, response.status

    assert status == expected_answer['status']
    assert body == expected_answer['response_body']


@pytest.mark.parametrize(
    'genre_id, expected_answer',
    [parametrize.genre_detail_parameters[0]]
)
@pytest.mark.asyncio
async def test_genre_cache(
    redis_client,
    es_write_data,
    make_get_request,
    genre_id: str,
    expected_answer: dict
):
    """
    Sends a request to the genre detail API endpoint
    and verifies that the Redis cache is working properly.
    """

    # Check that current Redis cache is empty
    assert await redis_client.keys('*') == []

    es_data = await es_queries.make_test_es_genres_data()
    await es_write_data(es_data, test_settings.es_genre_index)

    url = test_settings.service_url + f'genres/{genre_id}'
    await make_get_request(url)

    redis_key = f'genre:{genre_id}'
    data = json.loads(await redis_client.get(redis_key))

    assert len(await redis_client.keys('*')) == 1
    assert data == expected_answer['response_body']
