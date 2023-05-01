import json
import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers

from etl.utils.backoff_decorator import backoff
from etl.utils.etl_logging import logger
from etl.utils.settings import es_settings


load_dotenv()


class ElasticsearchLoader:
    def __init__(self, settings=es_settings):
        self.host = settings.ES_HOST
        self.port = settings.ES_PORT
        self.scheme = settings.ES_SCHEME
        self.film_index_name = settings.ES_INDEX
        self.genre_index_name = settings.ES_GENRE_INDEX
        self.client = Elasticsearch([{'scheme': self.scheme, 'host': self.host, 'port': self.port}])
        self.status = True if self.get_conn_status() else False
        self.film_schema = self.get_schema(file_path=settings.ES_SCHEMA)
        self.genre_schema = self.get_schema(file_path=settings.ES_GENRE_SCHEMA)
        self.indexes = self.get_indexes()

    @backoff(exception=ConnectionError)
    def get_conn_status(self):
        logger.info('Connecting to Elasticsearch...')
        if not self.client.ping():
            raise ConnectionError('No connection to Elasticsearch.')
        logger.info('Connected to Elasticsearch.')
        return True

    @staticmethod
    def get_schema(file_path: str):
        if os.path.exists(file_path):
            logger.info(f'File with an index schema found: {file_path}')
            with open(file_path) as json_file:
                return json.load(json_file)
        else:
            logger.warning("Index schema file '%s' not found.", file_path)
            return None

    @backoff(exception=ConnectionError)
    def get_indexes(self) -> list:
        indexes = list(self.client.indices.get_alias().keys())
        if self.film_index_name not in indexes:
            self.create_index(self.film_index_name)
            logger.info(f'Successfully created index {self.film_index_name}')
        if self.genre_index_name not in indexes:
            self.create_index(self.genre_index_name)
            logger.info(f'Successfully created index {self.genre_index_name}')
        return indexes

    def close(self):
        self.client.transport.close()
        logger.info('Elasticsearch connection closed.')

    def create_index(self, index_name: str):
        if 'movie' in index_name:
            body = self.film_schema
            if body:
                self.client.indices.create(index=index_name, body=body)
                logger.info(f'Index "{index_name}" created.')
            else:
                logger.warning(
                    'Index "%s" not created, no schema.', index_name
                )
        if 'genre' in index_name:
            body = self.genre_schema
            if body:
                self.client.indices.create(index=index_name, body=body)
                logger.info(f'Index "{index_name}" created.')
            else:
                logger.warning(
                    'Index "%s" not created, no schema.', index_name
                )

    @backoff(exception=ConnectionError)
    def transfer_films(self, actions) -> None:
        """Add data packets to Elasticsearch.

        """
        success, failed = helpers.bulk(
            client=self.client,
            actions=[
                {'_index': self.film_index_name, '_id': action.get('id'), **action}
                for action in actions
            ],
            stats_only=True
        )
        logger.info('Successfully transferred films: %s,'
                'failed to transfer: %s', success, failed)

    def transfer_genres(self, actions) -> None:
        """Add data packets to Elasticsearch.

        """
        success, failed = helpers.bulk(
            client=self.client,
            actions=[
                {'_index': self.genre_index_name, '_id': action.get('id'), **action}
                for action in actions
            ],
            stats_only=True
        )
        logger.info('Successfully transferred genres: %s,'
                'failed to transfer: %s', success, failed)


