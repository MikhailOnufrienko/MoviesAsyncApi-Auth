import pytest

from tests.functional.settings import test_settings
from tests.functional.utils import es_queries
from tests.functional.utils import parametrize


QUERY_EXIST = 'PYTESTFILMS'
QUERY_NOT_EXIST = 'NOTEXIST'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    parametrize.film_search_parameters
)
@pytest.mark.asyncio
async def test_search(
    es_write_data: callable,
    make_get_request: callable,
    query_data: dict,
    expected_answer: dict
):

    es_data = await es_queries.make_test_es_data(QUERY_EXIST)
    await es_write_data(es_data)

    url = test_settings.base_url + '/films/search'

    body, status = await make_get_request(url, query_data)

    assert status == expected_answer['status']
    assert body['total'] == expected_answer['length']
    assert (body['next'] is not None) == expected_answer['has_next_page']

    if expected_answer['has_next_page'] is True:
        url = test_settings.base_url + body['next']
        page2_query = {
            'query': QUERY_EXIST,
            'page_size': 10
        }
        body, status = await make_get_request(url, page2_query)

        assert body['prev'] is not None
        assert body['next'] is not None
