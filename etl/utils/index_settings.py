from elasticsearch import Elasticsearch

INDEX_SETTINGS = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },
    'mappings': {
        'properties': {
            'id': {
                'type': 'keyword'
            },
            'full_name': {
                'type': 'text',
            },
        }
    }
}


def create_es_index(es: Elasticsearch, index_name: str) -> None:
    """Создает ElasticSearch индекс по указанным параметрам"""

    es.indices.create(
        index=index_name,
        settings=INDEX_SETTINGS['settings'],
        mappings=INDEX_SETTINGS['mappings']
    )
