import pytest
from elasticsearch import AsyncElasticsearch
import aiohttp
# from redis import Redis
# from aioredis.client import Redis
import redis.asyncio as redis

from tests.functional.settings import test_settings
from tests.functional.utils.es_queries import get_es_bulk_query
from tests.functional.utils import indices


QUERY_EXIST = 'PYTESTFILMS'


# r = Redis()


@pytest.fixture(scope='function')
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.es_host)
    yield client
    await client.close()


@pytest.fixture(scope='function')
async def session_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='function')
async def redis_client():
    client = redis.Redis()
    await client.flushdb()
    yield client
    await client.close()


@pytest.fixture
def redis_cleare_cache(redis_client):

    async def inner():
        await redis_client.flushall()
    
    return inner


@pytest.fixture(scope='function')
async def run_after_each_test(redis_cleare_cache):
    await redis_cleare_cache()
    yield
    await redis_cleare_cache()


@pytest.fixture
def es_create_indices(es_client: AsyncElasticsearch):
    """pass"""

    async def inner(index_name: str):
        """pass"""

        if not await es_client.indices.exists(index=index_name):
            await es_client.indices.create(
                index=index_name,
                settings=indices.MOVIES_INDEX_SETTINGS['settings'],
                mappings=indices.MOVIES_INDEX_SETTINGS['mappings']
            )
        
    return inner


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch) -> callable:
    """Write test data into ElasticSearch index."""

    async def inner(es_data: list):
        """Function logic."""

        bulk_query = await get_es_bulk_query(
            es_data, test_settings.es_index, test_settings.es_id_field
        )
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(operations=str_query, refresh=True)

        if response['errors']:
            raise Exception('Error while loading to ElasticSearch')

    return inner


@pytest.fixture
def make_get_request(session_client: aiohttp.ClientSession) -> callable:
    """Send get request to api endpoint and return the response."""

    async def inner(url: str, query_data: dict):
        """Function logic."""

        async with session_client.get(url, params=query_data) as response:
            body = await response.json()
            status = response.status
            return body, status

    return inner


@pytest.fixture
async def delete_test_data(es_client: AsyncElasticsearch) -> callable:
    """Remove all testing data from ElasticSearch index."""

    async def inner(query_parameter: str):
        """Function logic."""

        try:
            await es_client.delete_by_query(
                index=test_settings.es_index,
                body={"query": {"match_phrase": {"title": query_parameter}}}
            )
        except Exception:
            pass

    return inner


# @pytest.fixture(autouse=True)
# async def run_before_tests(es_create_indices):
#     """"""

#     await es_create_indices('test')
#     yield


@pytest.fixture(autouse=True)
async def run_before_and_after_tests(
    delete_test_data: callable,
    es_create_indices: callable
) -> None:
    """Run functions after each test."""

    await es_create_indices(test_settings.es_index)

    yield

    await delete_test_data(QUERY_EXIST)
