from elasticsearch import Elasticsearch
from utils.index_settings import create_es_index
import os
from dotenv import load_dotenv
from pg_extractor import PostgresExtractor
import psycopg2
from psycopg2.extras import DictCursor
from es_loader import ESLoader
import logging
import pytz
import datetime
import redis
from utils.logging_settings import setup_logging
from utils.state import STATE_CLS

load_dotenv()

setup_logging()

es = Elasticsearch(hosts='http://localhost:9200/')

tz = pytz.timezone('Europe/Moscow')

BLOCK_SIZE = 500

PERSON_INDEX_NAME = 'person_index'

dsl = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
}


def run(extractor: PostgresExtractor, loader: ESLoader):
    """Extracting data from postgres and loading to ES."""

    start_time = tz.localize(datetime.datetime.now())


    for data in extractor.extract_data():

        logging.info('Data block fetched from PostgreSQL.')

        try:
            loader.load(data, PERSON_INDEX_NAME)
            logging.info(
                'Data loaded to ElasticSearch index: %s.', PERSON_INDEX_NAME
            )
        except Exception as exc:
            logging.exception('An error occured: %s', exc)


if __name__ == '__main__':

    if not es.indices.exists(index=PERSON_INDEX_NAME):
        create_es_index(es, PERSON_INDEX_NAME)
    
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:

        extractor = PostgresExtractor(pg_conn, BLOCK_SIZE)
        loader = ESLoader(es)

        run(extractor, loader)
