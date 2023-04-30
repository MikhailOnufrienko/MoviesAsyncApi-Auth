from elasticsearch import Elasticsearch
from utils.index_settings import create_es_index
import os
import time
from dotenv import load_dotenv
from services.pg_extractor import PostgresExtractor
import psycopg2
from psycopg2.extras import DictCursor
from services.es_loader import ESLoader
import logging
import pytz
import datetime
from utils.logging_settings import setup_logging
from utils.state import STATE_CLS
from services.config import ES_HOST, SLEEP_TIME

load_dotenv()

setup_logging()

es = Elasticsearch(hosts=ES_HOST)

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

    STATE_CLS.set_state(key='filmwork_ids', value=[])

    extract_time = datetime.datetime.strptime(
        STATE_CLS.get_state('modified_time'),
        '%Y-%m-%d %H:%M:%S.%f%z'
    )

    for data in extractor.extract_data(
        start_time=start_time,
        extract_time=extract_time,
        excluded_ids=STATE_CLS.get_state('filmwork_ids')
    ):

        logging.info('Data block fetched from PostgreSQL.')

        try:
            loader.load(data, PERSON_INDEX_NAME)
            logging.info(
                'Data loaded to ElasticSearch index: %s.', PERSON_INDEX_NAME
            )
        except Exception as exc:
            logging.exception('An error occured: %s', exc)
    
    STATE_CLS.set_state(key='modified_time', value=str(start_time))


if __name__ == '__main__':

    if not es.indices.exists(index=PERSON_INDEX_NAME):
        create_es_index(es, PERSON_INDEX_NAME)
    
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:

        extractor = PostgresExtractor(pg_conn, BLOCK_SIZE)
        loader = ESLoader(es)

        while True:

            try:
                run(extractor, loader)
                time.sleep(SLEEP_TIME)
            except Exception as exc:
                pg_conn.close()
                es.close()
                logging.exception('An error occured: %s', exc)
