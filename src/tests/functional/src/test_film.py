import pytest

from tests.functional.utils import es_queries, parametrize
from tests.functional.settings import test_settings
import redis.asyncio as redis
import json


@pytest.mark.parametrize(
    'genre_id, query_data, expected_answer',
    parametrize.films_by_genre_parameters
)
@pytest.mark.asyncio
async def test_films_by_genre_response(
    es_write_data: callable,
    make_get_request: callable,
    genre_id: str,
    query_data: dict,
    expected_answer: dict
) -> None:
    """
    Sends a request to the film API endpoint with a query by genre id
    and validates the given responses.
    """

    es_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_data, test_settings.es_movie_index)

    url = test_settings.service_url + f'films/'
    response = await make_get_request(url, query_data)
    body, status = response.body, response.status

    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert (body['next'] is not None) == expected_answer['has_next_page']

    if expected_answer['has_next_page'] is True:
        query_data = {
            'genre': genre_id,
            'page_number': 2,
            'page_size': 10
        }
        response = await make_get_request(url, query_data)
        body, status = response.body, response.status

        assert body['prev'] is not None
        assert body['next'] is not None


@pytest.mark.parametrize(
    'film_id, expected_answer',
    parametrize.film_detail_parameters
)
@pytest.mark.asyncio
async def test_film_detail_response(
    es_write_data: callable,
    make_get_request: callable,
    film_id: str,
    expected_answer: dict
) -> None:
    """
    Sends a request to the film detail API endpoint
    and validates the given responses.
    """

    es_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_data, test_settings.es_movie_index)

    url = test_settings.service_url + f'films/{film_id}'
    response = await make_get_request(url)
    body, status = response.body, response.status

    assert status == expected_answer['status']
    assert body == expected_answer['response_body']


@pytest.mark.asyncio
async def test_films_by_genre_redis_cache(
    redis_client: redis.Redis,
    make_get_request: callable,
    es_write_data: callable
) -> None:
    """
    Sends a request to the film API endpoint with a query by genre
    and verifies that the Redis cache is working properly.
    """

    # Check that current Redis cache is empty
    assert await redis_client.keys('*') == []

    es_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_data, test_settings.es_movie_index)

    url = test_settings.service_url + f'films/'
    query_data = {
        'genre': '120a21cf-9097-479e-904a-13dd7198c1dd',
        'page_number': 1,
        'page_size': 10
    }
    genre_id, page, size = query_data.values()
    
    await make_get_request(url, query_data)

    redis_key = f'films:{page}:{size}:{genre_id}:None'
    data = await redis_client.get(redis_key)
    data = json.loads(data)

    assert data is not None
    assert data['total'] == 50
    assert len(data['films']) == 10


@pytest.mark.parametrize(
    'film_id, expected_answer',
    [parametrize.film_detail_parameters[0]]
)
@pytest.mark.asyncio
async def test_film_detail_cache(
    redis_client: redis.Redis,
    es_write_data,
    make_get_request,
    film_id: str,
    expected_answer: dict
):
    """
    Sends a request to the film detail API endpoint
    and verifies that the Redis cache is working properly.
    """

    # Check that current Redis cache is empty
    assert await redis_client.keys('*') == []

    es_data = await es_queries.make_test_es_movie_data(
        existing_film_query=parametrize.FILM_QUERY_EXIST,
        existing_person_query=parametrize.PERSON_SINGLE_QUERY_EXIST
    )
    await es_write_data(es_data, test_settings.es_movie_index)

    url = test_settings.service_url + f'films/{film_id}'
    await make_get_request(url)
    
    redis_key = f'film:{film_id}'
    data = json.loads(await redis_client.get(redis_key))

    assert len(await redis_client.keys('*')) == 1
    assert data == expected_answer['response_body']
