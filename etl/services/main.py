import time
from datetime import datetime
from pathlib import Path
import pytz

from etl.utils import models_validation
from postgres_extractor import PostgresExtractor
from es_loader import ElasticsearchLoader
from etl.utils.etl_logging import logger
from etl.utils.etl_state import State, JsonFileStorage
from etl.utils.settings import etl_settings
from etl.services import config
from elasticsearch import Elasticsearch
from etl.utils.index_settings import create_es_index


es = Elasticsearch(hosts=config.ES_HOST)


class ETL:
    def __init__(self, settings=etl_settings, state=None):
        self.conf = settings
        self.state = state
        self.pg_client = None
        self.es_client = None
        self.states = None

    def __enter__(self):
        logger.info('ETL process started.')
        self.state.set_state('etl_process', 'started')

        try:
            self.pg_client = PostgresExtractor()
            self.es_client = ElasticsearchLoader(es=es)
        except Exception:
            self.state.set_state('etl_process', 'stopped')
            raise
        else:
            self.states = self.state.get_state('modified') or {}
            return self

    def __exit__(self, type, value, traceback):
        logger.info('Closing all connections...')
        if self.es_client is not None:
            self.es_client.close()

        if self.pg_client is not None:
            self.pg_client.close()

        logger.info('ETL process stopped.')
        self.state.set_state('etl_process', 'stopped')

        logger.info('Load paused for %s seconds', etl_settings.LOAD_PAUSE)
        time.sleep(self.conf.LOAD_PAUSE)

    def extract_films(self) -> tuple:
        """
        Retrieve all new or modified data
        (genres, characters and movies) from PostgreSQL.
        Return the number of unique movie ids and movie instances.

        """
        genre_filmwork_ids: list[str] = []
        person_filmwork_ids: list[str] = []
        filmwork_ids: list[str] = []
        modified_genre: str = self.states.get('genre') or datetime.min
        modified_person: str = self.states.get('person') or datetime.min
        modified_filmwork: str = self.states.get('filmwork') or datetime.min

        genres = self.pg_client.fetch_modified_genres(
            timestamp=modified_genre
        )
        if genres:
            self.states['genre'] = f'{genres[-1].modified}'
            genre_filmwork_ids = self.pg_client.fetch_filmworks_by_modified_genres(
                genres=[genre.id for genre in genres])

        persons = self.pg_client.fetch_modified_persons(
            timestamp=modified_person
        )
        if persons:
            self.states['person'] = f'{persons[-1].modified}'
            person_filmwork_ids = self.pg_client.fetch_filmworks_by_modified_persons(
                persons=[person.id for person in persons])

        filmworks = self.pg_client.fetch_modified_filmworks(
            timestamp=modified_filmwork
        )
        if filmworks:
            self.states['filmwork'] = f'{genres[-1].modified}'
            filmwork_ids = [filmwork.id for filmwork in filmworks]

        unique_filmwork_ids = set(
            filmwork_ids + person_filmwork_ids + genre_filmwork_ids
        )

        filmwork_instances = self.pg_client.fetch_filmworks_by_id(
            ids=tuple(unique_filmwork_ids)
        )
        return len(unique_filmwork_ids), filmwork_instances

    def extract_genres(self) -> tuple:
        """
        Retrieve all new or modified data (genres) from PostgreSQL.
        Return the number of unique genre ids and genre instances.

        """

        modified_genre2: str = self.states.get('genre2') or datetime.min

        genres = self.pg_client.fetch_genres_with_films(
	        timestamp=modified_genre2
        )

        if genres:
            self.states['genre2'] = f'{genres[-1]["modified"]}'
    
#       unique_genre_ids = [genre.id for genre in genres]
#       genre_instances = self.pg_client.fetch_genres_by_id(ids=tuple(unique_genre_ids))

        return len(genres), genres

    def transform_films(self, modified_data):
        """
        Transform extracted movie instances for Elasticsearch.
        Generate a list of unique movies along with grouping of lists and
        instances genre, director, actor, writer.

        """
        if modified_data is not None:
            transformed_data: list = []
            filmwork_ids: set = {filmwork.get('fw_id')
                                 for filmwork in modified_data}
            for filmwork_id in filmwork_ids:
                genres: list[dict[str, str]] | list = []
                directors: list[dict[str, str]] | list = []
                actors_names: list[str] | list = []
                writers_names: list[str] | list = []
                actors: list[dict[str, str]] | list = []
                writers: list[dict[str, str]] | list = []
                for filmwork in modified_data:
                    if filmwork.get('fw_id') == filmwork_id:
                        imdb_rating = filmwork.get('rating')
                        title = filmwork.get('title')
                        description = filmwork.get('description')
                        genre_instance = {'id': filmwork.get('genre_id'),
                                           'name': filmwork.get('genre')}
                        if genre_instance not in genres:
                            genres.append(genre_instance)
                        person_name = filmwork.get('full_name')
                        person_instance = {'id': filmwork.get('person_id'),
                                           'name': person_name}
                        if filmwork.get('role') == 'director':
                            if person_instance not in directors:
                                directors.append(person_instance)
                        elif filmwork.get('role') == 'actor':
                            if person_name not in actors_names:
                                actors_names.append(person_name)
                            if person_instance not in actors:
                                actors.append(person_instance)
                        elif filmwork.get('role') == 'writer':
                            if person_name not in writers_names:
                                writers_names.append(person_name)
                            if person_instance not in writers:
                                writers.append(person_instance)
                        new_filmwork = {
                            'id': filmwork_id,
                            'imdb_rating': imdb_rating,
                            'title': title,
                            'description': description,
                            'genre': genres,
                            'director': directors,
                            'actors_names': actors_names,
                            'writers_names': writers_names,
                            'actors': actors,
                            'writers': writers,
                        }

                transformed_data.append(new_filmwork)
            for filmwork in transformed_data:
                yield models_validation.ESFilmworkModel(**filmwork).dict()

    def transform_genres(self, modified_data):
        """
        Transform extracted genre instances for Elasticsearch.
        Generate a list of unique genres with a list of filmwork IDs.

        """

        if modified_data is not None:
            transformed_data: list = []
            for genre in modified_data:
                new_genre = {
                    'id': genre.get('id'),
                    'name': genre.get('name'),
                    'description': genre.get('description')
                }
                transformed_data.append(new_genre)
            for genre in transformed_data:
                yield models_validation.ESGenreAndFilmModel(**genre).dict()

    def load_films(self, transformed_data):
        """
        Generate movie packets and upload them to Elasticsearch.

        """
        actions: list = []
        for data in transformed_data:
            actions.append(data)
            if len(actions) == self.conf.LIMIT:
                self.es_client.transfer_films(actions=actions)
                actions.clear()
        else:
            if actions:
                self.es_client.transfer_films(actions=actions)
                pass

    def load_genres(self, transformed_data):
        """
        Generate genre packets and upload them to Elasticsearch.

        """
        actions: list = []
        for data in transformed_data:
            actions.append(data)
            if len(actions) == self.conf.LIMIT:
                self.es_client.transfer_genres(actions=actions)
                actions.clear()
        else:
            if actions:
                logger.info(f'actions to transfer: {actions}')
                self.es_client.transfer_genres(actions=actions)
                pass
    
    def extract_load_persons(self):
        """Retrieve modified and new persons data from PostgreSQL."""

        tz = pytz.timezone('Europe/Moscow')
        start_time = tz.localize(datetime.datetime.now())
        modified_timestamp = self.states.get('persons') or datetime.min

        persons = self.pg_client.get_persons(modified_timestamp)

        for data in persons:
            logger.info('Persons Data Block fetched')

            try:
                self.es_client.load_persons(data, 'person_index')
                logger.info('Persons Data Block Loaded to ES.')
            except Exception as exc:
                logger.exception(exc)

        if persons:
            self.states['persons'] = str(start_time)

    def save_state(self):
        """Save the last ETL state.

        """
        self.state.set_state('modified', self.states)


# ETL state storage settings
default_file_path: str = f'{Path(__file__).resolve().parent}'
storage = JsonFileStorage(file_path=default_file_path,
                          file_name=etl_settings.STATE_FILE_NAME)


def load_to_es():
    while True:
        with ETL(state=State(storage=storage)) as etl:

            logger.info('Starting extraction of films from PostgreSQL.')
            number_data, modified_data = etl.extract_films()
            logger.info('Extracted %d modified films.', number_data)

            if modified_data is not None:
                transformed_data = etl.transform_films(modified_data=modified_data)
                logger.info('Starting films transfer to Elasticsearch.')

                etl.load_films(transformed_data=transformed_data)
                logger.info('Saving state.')

                etl.save_state()
            else:
                logger.info('No films to load into Elasticsearch.')

            logger.info('Starting extraction of genres from PostgreSQL.')
            number_data, modified_data = etl.extract_genres()
            logger.info('Extracted %d modified genres.', number_data)

            if modified_data is not None:
                transformed_data = etl.transform_genres(modified_data=modified_data)
                logger.info('Starting genres transfer to Elasticsearch.')

                etl.load_genres(transformed_data=transformed_data)
                logger.info('Saving state.')

                etl.save_state()
            else:
                logger.info('No genres to load into Elasticsearch.')
            
            etl.extract_load_persons()

if __name__ == '__main__':
    if not es.indices.exists(index='person_index'):
        create_es_index(es, 'person_index')
    try:
        load_to_es()
    except KeyboardInterrupt:
        logger.info('ETL process interrupted.')
