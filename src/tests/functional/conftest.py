import asyncio

import pytest
import redis.asyncio as redis

from tests.functional.utils import indices


pytest_plugins = [
    'tests.functional.fixtures.fixture_connection',
    'tests.functional.fixtures.fixture_es_actions',
    'tests.functional.fixtures.fixture_api_actions',
]


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope='session')
async def run_before_after_tests(
    es_create_indices: callable, es_delete_indices: callable
) -> None:
    """Run actions before and after all tests."""

    indices_names = ['movies', 'genres', 'persons']

    for index in indices_names:
        await es_create_indices(index, indices.index_to_schema[index])

    yield

    for index in indices_names:
        await es_delete_indices(index)
