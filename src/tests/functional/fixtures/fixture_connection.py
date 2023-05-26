import aiohttp
import pytest
import redis.asyncio as redis

from elasticsearch import AsyncElasticsearch
from tests.functional.settings import test_settings


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=test_settings.es_host)
    yield client
    await client.close()


@pytest.fixture(scope='function')
async def redis_client():
    client = redis.Redis(host='localhost', port=6379)
    await client.flushdb()
    yield client
    await client.flushall()
    await client.close()


@pytest.fixture(scope='function')
async def session_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()
