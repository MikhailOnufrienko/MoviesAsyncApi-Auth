import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.conftest import es_write_data, delete_test_data
from tests.functional.utils import es_queries
from tests.functional.utils import parametrize


QUERY_EXIST = 'PYTESTFILMS'
QUERY_NOT_EXIST = 'NOTEXIST'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    parametrize.film_search_parameters
)
@pytest.mark.asyncio
async def test_search(es_write_data, make_get_request, query_data, expected_answer):

    es_data = await es_queries.make_test_es_data(QUERY_EXIST)
    await es_write_data(es_data)

    url = test_settings.base_url + '/films/search'

    body, headers, status = await make_get_request(url, query_data)

    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert body['next'] == expected_answer['has_next_page']

    # assert status == 201

    # try:
    #     assert status == 200
    #     assert status == 201
    # finally:
    #     delete_test_data(QUERY_EXIST)

    # try:
    #     assert status == 200
    #     assert body['total'] == 50
    # except Exception:
    # # assert body['total'] == 50

    # await delete_test_data(QUERY_EXIST)
    #     raise Exception('123')
