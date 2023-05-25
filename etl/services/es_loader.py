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
        self.settings = settings
        self.client = Elasticsearch(
            [{
                'scheme': settings.ES_SCHEME,
                'host': settings.ES_HOST,
                'port': settings.ES_PORT
            }]
        )
        self.film_index_name = settings.ES_MOVIE_INDEX
        self.genre_index_name = settings.ES_GENRE_INDEX
        self.person_index_name = settings.ES_PERSON_INDEX
        self.status = True if self.get_conn_status() else False
        self.indices = self.create_es_indices()

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

    def close(self):
        self.client.transport.close()
        logger.info('Elasticsearch connection closed.')

    @backoff(exception=ConnectionError)
    def create_es_indices(self):
        """Create ES indices if they do not exist."""

        film_schema = self.get_schema(self.settings.ES_MOVIE_SCHEMA)
        genre_schema = self.get_schema(self.settings.ES_GENRE_SCHEMA)
        person_schema = self.get_schema(self.settings.ES_PERSON_SCHEMA)
        indices_schemas = {
            self.film_index_name: film_schema,
            self.person_index_name: person_schema,
            self.genre_index_name: genre_schema
        }

        for index_name, index_body in indices_schemas.items():
            if not self.client.indices.exists(index=index_name):
                if index_body:
                    self.client.indices.create(
                        index=index_name, body=index_body
                    )
                    logger.info(f'Index "{index_name}" successfully created.')
                else:
                    logger.warning('No schema for index "%s".', index_name)

    @backoff(exception=ConnectionError)
    def transfer_films(self, actions) -> None:
        """Add data packets to Elasticsearch."""

        success, failed = helpers.bulk(
            client=self.client,
            actions=[{
                '_index': self.film_index_name,
                '_id': action.get('id'),
                **action,
            } for action in actions],
            stats_only=True
        )
        logger.info(
            'Successfully transferred films: %s, failed to transfer: %s',
            success, failed
        )

    @backoff(exception=ConnectionError)
    def transfer_persons(self, actions) -> None:
        """Add data packets to Elasticsearch."""

        success, failed = helpers.bulk(
            client=self.client,
            actions=[{
                '_index': self.person_index_name,
                '_id': action.get('id'),
                **action,
            } for action in actions],
            stats_only=True
        )
        logger.info(
            'Successfully transferred persons: %s, failed to transfer: %s',
            success, failed
        )

    @backoff(exception=ConnectionError)
    def transfer_genres(self, actions) -> None:
        """Add data packets to Elasticsearch."""

        success, failed = helpers.bulk(
            client=self.client,
            actions=[{
                '_index': self.genre_index_name,
                '_id': action.get('id'),
                **action,
            } for action in actions],
            stats_only=True
        )
        logger.info(
            'Successfully transferred genres: %s, failed to transfer: %s',
            success, failed
        )
