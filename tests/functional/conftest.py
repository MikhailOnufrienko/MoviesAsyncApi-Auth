
import json
import uuid

from elasticsearch import AsyncElasticsearch
import pytest
import requests
import aioredis
import aiohttp
# from redis import Redis
# from aioredis.client import Redis
import redis.asyncio as redis

from tests.functional.settings import test_settings

from tests.functional.utils.es_queries import get_es_bulk_query
from tests.functional.utils import indices

# from etl.utils.backoff_decorator import backoff
# from .utils.indices import index_to_schema
# from .utils import models



def delete_data_from_elastic(url_elastic: str, urls: list[str]) -> None:
    for url in urls:
        requests.delete(f'{url_elastic}/{url}')


# @backoff(exception=ConnectionError)
@pytest.fixture(scope='function')
async def es_client():
    url_elastic: str = test_settings.es_host
    client = AsyncElasticsearch(hosts=url_elastic)
    yield client
    await client.close()
    delete_data_from_elastic(url_elastic, ['genre', 'persons'])


@pytest.fixture(scope='function')
async def redis_client():
    redis_host: str = test_settings.redis_host
    redis = await aioredis.create_redis_pool(
        redis_host, minsize=10, maxsize=20
    )
    yield redis
    redis.close()
    await redis.wait_closed()


@backoff(exception=ConnectionError)
async def create_index(es_client):
    """Create indices for testing purposes.

    """
    for index in ("genres", "persons"):
        data_create_index = {
            "index": index,
            "ignore": 400,
            "body": index_to_schema.get(index)
        }
        await es_client.indices.create(
            **data_create_index
        )


@pytest.fixture(scope='function')
async def session():
# import pytest
# from elasticsearch import AsyncElasticsearch
# import aiohttp

# from tests.functional.settings import test_settings
# from tests.functional.utils.es_queries import get_es_bulk_query


# QUERY_EXIST = 'PYTESTFILMS'


# @pytest.fixture(scope='function')
# async def es_client():
#     client = AsyncElasticsearch(hosts=test_settings.es_host)
#     yield client
#     await client.close()


# @pytest.fixture(scope='function')
# async def session_client():

    session = aiohttp.ClientSession()
    yield session
    await session.close()



# @pytest.fixture(scope='function')
# async def redis_client():
#     client = redis.Redis()
#     await client.flushdb()
#     yield client
#     await client.flushall()
#     await client.close()


# @pytest.fixture
# def es_create_indices(es_client: AsyncElasticsearch):
#     """pass"""

#     async def inner(index_name: str, index_body: dict):
#         """pass"""

#         if not await es_client.indices.exists(index=index_name):
#             await es_client.indices.create(
#                 index=index_name,
#                 settings=index_body['settings'],
#                 mappings=index_body['mappings']
#             )
        
#     return inner


# @pytest.fixture
# def es_write_data(es_client: AsyncElasticsearch) -> callable:
#     """Write test data into ElasticSearch index."""

#     async def inner(es_data: list, index_name: str):
#         """Function logic."""

#         bulk_query = await get_es_bulk_query(
#             es_data, index_name, test_settings.es_id_field
#         )
#         str_query = '\n'.join(bulk_query) + '\n'
#         response = await es_client.bulk(operations=str_query, refresh=True)


# def get_es_bulk_query(es_data, es_index, es_id_field):
#     bulk_query = []
#     for row in es_data:
#         bulk_query.extend([
#             json.dumps(
#                 {'index': {'_index': es_index, '_id': row[es_id_field]}}
#             ),
#             json.dumps(row)
#         ])
#     return '\n'.join(bulk_query) + '\n'



@pytest.fixture
def es_write_data(es_client):
    async def inner(data: list[dict], es_index: str):
        bulk_query = get_es_bulk_query(
            data, es_index, test_settings.es_id_field
        )
        response = await es_client.bulk(body=bulk_query, refresh=True)
        if response['errors']:
            raise Exception('Error: failed to write data into Elasticsearch.')

# @pytest.fixture
# def es_write_data(es_client: AsyncElasticsearch) -> callable:
#     """Write test data into ElasticSearch index."""

#     async def inner(es_data: list):
#         """Function logic."""

#         bulk_query = await get_es_bulk_query(
#             es_data, test_settings.es_index, test_settings.es_id_field
#         )
#         str_query = '\n'.join(bulk_query) + '\n'
#         response = await es_client.bulk(operations=str_query, refresh=True)

#         if response['errors']:
#             raise Exception('Error while loading to ElasticSearch')


    return inner


@pytest.fixture
def make_get_request(session):
    async def inner(endpoint: str, params: dict = {}) -> models.HTTPResponse:
        url = f"{test_settings.service_url}{endpoint}"
        async with session.get(url, params=params) as response:
            return models.HTTPResponse(
                body=await response.json(),
                status=response.status,
            )

# def make_get_request(session_client: aiohttp.ClientSession) -> callable:
#     """Send get request to api endpoint and return the response."""

#     async def inner(url: str, query_data: dict):
#         """Function logic."""

#         async with session_client.get(url, params=query_data) as response:
#             body = await response.json()
#             status = response.status
#             return body, status


    return inner


@pytest.fixture


#     async def inner(query: dict, index_name):
#         """Function logic."""

#         try:
#             await es_client.delete_by_query(
#                 index=index_name,
#                 query=query
#             )
#         except Exception:
#             pass

# def generate_es_data_genre():
#     """Generate genre data.

#     """
#     genres = [
#         {
#             'id': str(uuid.uuid4()),
#             'name': 'Comedy',
#             'description': 'Movies to make you laugh:)'
#         } for _ in range(9)
#     ]
#     genres.append(
#         {
#             'id': '120a21cf-9097-479e-904a-13dd7198c1dd',
#             'name': 'Adventure',
#             'description': 'Exciting and unusual experience.'
#         }
#     )
#     return genres



@pytest.fixture
def generate_es_data_person():
    """Generate person data.

    """
    persons = [
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Robin Williams',
        }
        for _ in range(60)
    ]
    persons.extend([
        {'id': '32b50c6b-4907-292f-b652-6ef2ee8b43f8',
         'full_name': 'Robin Williams'}
    ])
    return persons

# async def delete_test_data(es_client: AsyncElasticsearch) -> callable:
#     """Remove all testing data from ElasticSearch index."""

#     async def inner(query_parameter: str):
#         """Function logic."""

#         await es_client.delete_by_query(
#             index=test_settings.es_index,
#             body={"query": {"match_phrase": {"title": query_parameter}}}
#         )

#     return inner


# @pytest.fixture(autouse=True)
# async def run_after_tests(delete_test_data: callable) -> None:
#     """Run functions after each test."""


# @pytest.fixture(autouse=True)
# async def run_before_and_after_tests(
#     delete_test_data: callable,
#     es_create_indices: callable
# ) -> None:
#     """Run functions after each test."""

#     await es_create_indices(test_settings.es_movie_index, indices.MOVIES_INDEX_SETTINGS)
#     await es_create_indices(test_settings.es_genre_index, indices.GENRES_INDEX_SETTINGS)
#     await es_create_indices(test_settings.es_person_index, indices.PERSONS_INDEX_SETTINGS)

#     yield

#     await delete_test_data({"match_phrase": {"title": QUERY_EXIST}}, test_settings.es_movie_index)
#     await delete_test_data({"match_phrase": {"full_name":'Random Name'}}, test_settings.es_person_index)
#     await delete_test_data({"match_phrase": {"full_name":'Single Name'}}, test_settings.es_person_index)

#     yield
#     await delete_test_data(QUERY_EXIST)
