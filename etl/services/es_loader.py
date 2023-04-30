from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ESLoader:

    def __init__(self, es: Elasticsearch) -> None:
        self.es = es

    def load(self, data: list, index_name: str) -> None:
        """Loading data to ES."""

        actions = []

        for item in data:
            action = {
                '_op_type': 'update',
                '_index': index_name,
                '_id': item['id'],
                'doc': item,
                'doc_as_upsert': True
            }
            actions.append(action)

        bulk(self.es, actions)
