import json
import uuid

from elasticsearch import AsyncElasticsearch
import pytest
import requests
import aioredis
import aiohttp

from tests.functional.settings import test_settings
from etl.utils.backoff_decorator import backoff
from .utils.indices import index_to_schema
from .utils import models


def delete_data_from_elastic(url_elastic: str, urls: list[str]) -> None:
    for url in urls:
        requests.delete(f'{url_elastic}/{url}')

# @backoff(exception=ConnectionError)
@pytest.fixture(scope='function')
async def es_client():
    url_elastic: str = test_settings.es_host
    client = AsyncElasticsearch(hosts=url_elastic, timeout=30)
    yield client
    await client.close()
    delete_data_from_elastic(url_elastic, ['persons', 'genre'])

@pytest.fixture(scope='function')
async def redis_client():
    redis_host: str = test_settings.redis_host
    redis = await aioredis.create_redis_pool(redis_host, minsize=10, maxsize=20)
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
    session = aiohttp.ClientSession()
    yield session
    await session.close()


def get_es_bulk_query(es_data, es_index, es_id_field):
    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': es_index, '_id': row[es_id_field]}}),
            json.dumps(row)
        ])
    return '\n'.join(bulk_query) + '\n'


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: list[dict], es_index: str):
        bulk_query = get_es_bulk_query(data, es_index, test_settings.es_id_field)
        response = await es_client.bulk(bulk_query, refresh=True)
        if response['errors']:
            raise Exception(f'Error: failed to write data into Elasticsearch.')
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
    return inner

@pytest.fixture
def generate_es_data_genre():
    """Generate genre data.
    
    """
    genres = [
            {
                'id': str(uuid.uuid4()),
                'name': 'Comedy',
                'description': 'Movies to make you laugh:)'
            }
            for _ in range(9)
        ]
    genres.append(
        {
            'id': '120a21cf-9097-479e-904a-13dd7198c1dd',
            'name': 'Adventure',
            'description': 'Exciting and unusual experience.'
        }
    )
    return genres
