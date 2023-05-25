import time

from elasticsearch import Elasticsearch

from ..settings import test_settings


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=test_settings.es_host)

    while True:
        print('trying to access elastic search')
        if es_client.ping():
            break
        print('elastic search connection error')
        time.sleep(1)
