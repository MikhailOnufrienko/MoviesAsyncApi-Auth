import pytest
from elasticsearch import AsyncElasticsearch
import aiohttp

from tests.functional.settings import test_settings
from tests.functional.utils.es_queries import get_es_bulk_query


QUERY_EXIST = 'PYTESTFILMS'


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

        await es_client.delete_by_query(
            index=test_settings.es_index,
            body={"query": {"match_phrase": {"title": query_parameter}}}
        )

    return inner


@pytest.fixture(autouse=True)
async def run_after_tests(delete_test_data: callable) -> None:
    """Run functions after each test."""

    yield
    await delete_test_data(QUERY_EXIST)
