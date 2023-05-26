import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.utils.es_queries import get_es_bulk_query


@pytest.fixture(scope='session')
def es_create_indices(es_client: AsyncElasticsearch):
    """pass"""

    async def inner(index_name: str, index_body: dict):
        """pass"""

        if not await es_client.indices.exists(index=index_name):
            await es_client.indices.create(
                index=index_name,
                settings=index_body['settings'],
                mappings=index_body['mappings']
            )

    return inner


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch) -> callable:
    """Write test data into ElasticSearch index."""

    async def inner(data: list[dict], es_index_name: str):
        """Function logic."""

        bulk_query = await get_es_bulk_query(
            data, es_index_name, test_settings.es_id_field
        )
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(operations=str_query, refresh=True)

        if response['errors']:
            raise Exception('Error: failed to write data into Elasticsearch.')

    return inner


@pytest.fixture(scope='session')
def es_delete_indices(es_client: AsyncElasticsearch) -> callable:
    """pass."""

    async def inner(es_index_name: str):
        """Function logic."""

        if await es_client.indices.exists(index=es_index_name):
            await es_client.indices.delete(index=es_index_name)

    return inner


@pytest.fixture(autouse=True, scope='function')
async def delete_es_data(es_client: AsyncElasticsearch) -> None:
    """Clear ElasticSearch indices data after each test."""

    indices_names = ['movies', 'genres', 'persons']
    query = {'match_all': {}}

    for index_name in indices_names:
        try:
            await es_client.delete_by_query(
                index=index_name, query=query
            )
        except Exception:
            pass
