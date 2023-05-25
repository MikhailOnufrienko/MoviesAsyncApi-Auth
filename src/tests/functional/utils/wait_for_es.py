import time

from elasticsearch import Elasticsearch


if __name__ == '__main__':
    es_client = Elasticsearch(hosts='http://elastic_search:9200')

    while True:
        print('trying to access elastic search')
        if es_client.ping():
            break
        print('elastic search connection error')
        time.sleep(1)
