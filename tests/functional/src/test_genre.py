from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture

from ..conftest import create_index


@pytest.mark.parametrize(
    'expected_answer, es_data',
    [
        (
            10,
            lazy_fixture('generate_es_data_genre')
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_all_genres(
    es_client, es_write_data,
    make_get_request, expected_answer, es_data
):
    """Test API of all genres list.

    """
    await create_index(es_client)
    await es_write_data(data=es_data, es_index='genres')
    response = await make_get_request('genres')
    assert len(response.body) == expected_answer
    assert response.status == HTTPStatus.OK, f'{response.status} must be 200'


@pytest.mark.parametrize(
    'uuid_genre, expected_answer, es_data',
    [
        (
            '9c91a5b2-eb70-4889-8581-ebe427370edd',
            {'uuid': '120a21cf-9097-479e-904a-13dd7198c1dd',
             'name': 'Adventure'},
            lazy_fixture('generate_es_data_genre')
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_genre_by_id(
    es_client, es_write_data,
    make_get_request, uuid_genre,
    expected_answer, es_data
):
    """Test API for genre details.

    """
    await create_index(es_client)
    await es_write_data(es_data, 'genres')
    response = await make_get_request(f'genres/{uuid_genre}')
    assert response.body == expected_answer
    assert response.status == HTTPStatus.OK, f'{response.status} must be 200'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'uuid': '7283ch9k-4059-098r-751m-7dh490lk220n'},
            HTTPStatus.NOT_FOUND
        ),
    ]
)
@pytest.mark.asyncio
async def test_non_existing_genre(
    make_get_request, query_data, expected_answer
):
    """Test API for a non-existing genre.

    """
    response = await make_get_request(f'genres/{query_data}')
    assert expected_answer == response.status


@pytest.mark.parametrize(
    'expected_answer, es_data',
    [
        (
            10,
            lazy_fixture('generate_es_data_genre')
        ),
    ]
)
@pytest.mark.asyncio
async def test_genre_cache(
        es_client, redis_client, es_write_data,
        make_get_request, expected_answer, es_data
):
    """Test cache.

    """
    await create_index(es_client)
    await es_write_data(es_data, 'genres')
    await redis_client.flushall(async_op=True)
    keys = await redis_client.keys(pattern='*')

    assert len(keys) == 0

    response = await make_get_request('genres')
    keys = await redis_client.keys(pattern='*')

    assert len(keys) == 1
    assert expected_answer == len(response.body)
    assert response.status == HTTPStatus.OK, f'{response.status} must be 200'
