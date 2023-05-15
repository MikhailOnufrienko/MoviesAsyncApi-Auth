import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from tests.functional.settings import test_settings
from tests.functional.conftest import es_write_data, delete_test_data
from tests.functional.utils import es_queries


QUERY_EXIST = 'PYTESTFILMS'
QUERY_NOT_EXIST = 'NOTEXIST'


# @pytest.mark.parametrize(
#     'query_data, expected_answer',
#     [
#         (
#             {'query': QUERY_EXIST, 'page_number': 1, 'page_size': 10},
#             {'status': 200, 'length': 50}
#         ),
#         (
#             {'query': QUERY_NOT_EXIST, 'page_number': 1, 'page_size': 10},
#             {'status': 200, 'length': 0}
#         )
#     ]
# )


@pytest.mark.asyncio
async def test_search(es_write_data, delete_test_data, make_get_request):

    es_data = await es_queries.make_test_es_data(QUERY_EXIST)

    await es_write_data(es_data)

    url = 'http://127.0.0.1:8000/api/v1/films/search'

    query_data = {'query': QUERY_EXIST, 'page_number': 1, 'page_size': 10}

    response = await make_get_request(url, query_data)

    status = response.status



    # async with session.get(url, params=query_data) as response:
    #     body = await response.json()
    #     headers = response.headers
    #     status = response.status

    assert status == 200

    # assert body['total'] == expected_answer['length']

    await delete_test_data(QUERY_EXIST)

    # await es_client.delete_by_query(
    #     index=test_settings.es_index,
    #     body={"query": {"match_phrase": {"title": QUERY_EXIST}}}
    # )
    
    # await es_client.close()
