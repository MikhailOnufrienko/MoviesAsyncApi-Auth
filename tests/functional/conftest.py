import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
import aiohttp

from tests.functional.settings import test_settings
from tests.functional.utils.es_queries import get_es_bulk_query


@pytest.fixture(scope='function')
async def es_client():
    client = AsyncElasticsearch(hosts='http://127.0.0.1:9200')
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def es_write_data(es_client):
    async def inner(es_data: list):
        # response = await async_bulk(
        #     client=es_client, actions=str_query
        # )
        # client = AsyncElasticsearch(hosts='http://127.0.0.1:9200')
        bulk_query = await get_es_bulk_query(es_data, test_settings.es_index, test_settings.es_id_field)
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(operations=str_query, refresh=True)
        # await client.close()
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest.fixture
def make_get_request(session_client: aiohttp.ClientSession):
    async def inner(url: str, query_data: dict):
        async with session_client.get(url, params=query_data) as response:
            return response
    return inner


@pytest.fixture
async def delete_test_data(es_client: AsyncElasticsearch):
    async def inner(query_parameter: str):
        await es_client.delete_by_query(
            index=test_settings.es_index,
            body={"query": {"match_phrase": {"title": query_parameter}}}
        )
    return inner

