from elasticsearch import Elasticsearch
from utils.index_settings import create_es_index


es = Elasticsearch(hosts='http://elastic_search:9200/')

BLOCK_SIZE = 500

INDEX_NAME = 'person_index'


if __name__ == '__main__':
    
    if not es.indices.exists(index=INDEX_NAME):
        create_es_index(es, INDEX_NAME)
