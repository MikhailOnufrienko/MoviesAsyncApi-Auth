import time

from elasticsearch import ConnectionError, Elasticsearch

from src.tests.functional.utils.backoff import backoff
from src.tests.functional.settings import test_settings


@backoff(ConnectionError)
def check_elastic_conn(client: Elasticsearch):
    if not client.ping():
        raise ConnectionError


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=test_settings.es_host, request_timeout=300)
    check_elastic_conn(es_client)
