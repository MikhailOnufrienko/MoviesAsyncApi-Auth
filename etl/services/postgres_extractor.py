import psycopg2
from dotenv import load_dotenv
from psycopg2 import OperationalError
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

from etl.utils import models_validation
from etl.utils import queries
from etl.utils.backoff_decorator import backoff
from etl.utils.etl_logging import logger
from etl.utils.settings import pg_settings, etl_settings


load_dotenv()


class PostgresConnector:
    def __init__(self, settings=pg_settings):
        self.dsn: dict = {
            'dbname': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'options': settings.DB_OPTIONS
        }
        self.conn: connection | None

    def connect(self) -> connection:
        return psycopg2.connect(**self.dsn, cursor_factory=DictCursor)


class PostgresExtractor:
    def __init__(self):
        self.state: etl_settings.STATE
        self.conn: connection = self.connect_to_pg()

    @backoff(exception=OperationalError)
    def connect_to_pg(self):
        logger.info('Connecting to PostgreSQL...')
        with PostgresConnector().connect() as conn:
            logger.info('Connected to PostgreSQL.')
            return conn

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info('Connection to PostgreSQL closed.')

    def execute_query(self, query):
        """Execute a query to PostgreSQL database and return a result.

        """
        with self.conn.cursor() as curs:
            curs.execute(query)
            return curs.fetchall()

    def fetch_modified_genres(self, timestamp):
        """Return a list with movies' genres modified or added anew.

        """
        genres = self.execute_query(
            query=queries.get_modified_genres(timestamp=timestamp)
        )
        if genres:
            return [
                models_validation.PGGenreModel(**genre)
                for genre in genres
            ]
        return []

    def fetch_filmworks_by_modified_genres(
        self,
        genres: list[str]
    ) -> list[str]:
        """Return movies if corresponding genres have been modified.

        """
        filmworks = self.execute_query(
            query=queries.get_modified_filmworks_by_genres(genres=genres)
        )
        return [
            models_validation.PGGenreFilmworkModel(
                **filmwork
            ).id for filmwork in filmworks
        ]

    def get_persons(self, timestamp) -> list:
        """Return a list with persons data.

        """
        query = queries.get_persons(timestamp)

        with self.conn.cursor() as curs:
            curs.execute(query)

        while True:
            data = curs.fetchmany(size=200)
            if not data:
                break

            yield [dict(row) for row in data]

        curs.close()

    def fetch_modified_persons(self, timestamp) -> list:
        """Return a list with movies' personnel modified or added anew.

        """
        persons = self.execute_query(
            query=queries.get_modified_persons(timestamp=timestamp)
        )
        if persons:
            return [
                models_validation.PGPersonModel(**person)
                for person in persons
            ]
        return []

    def fetch_filmworks_by_modified_persons(
        self, persons: list[str]
    ) -> list[str]:
        """Return movies if corresponding personnel has been modified.

        """
        filmworks = self.execute_query(
            query=queries.get_modified_filmworks_by_persons(persons=persons)
        )
        return [
            models_validation.PGPersonFilmworkModel(
                **filmwork
            ).id for filmwork in filmworks
        ]

    def fetch_modified_filmworks(self, timestamp) -> list:
        """Return a list with movies modified or added anew.

        """
        filmworks = self.execute_query(
            query=queries.get_modified_filmworks(timestamp=timestamp)
        )
        if filmworks:
            return [
                models_validation.PGFilmworkModel(**filmwork)
                for filmwork in filmworks
            ]
        return []

    def fetch_filmworks_by_id(self, ids: tuple) -> list[tuple] | None:
        """Return movies' instances.

        """
        if ids:
            return self.execute_query(
                query=queries.get_filmwork_by_id(ids=ids)
            )
        return None

    def fetch_genres_with_films(self, timestamp: int) -> list[tuple]:
        """Return genres' instances.

        """
        genres = self.execute_query(
            query=queries.get_genres(timestamp=timestamp)
        )
        if genres:
            return [
                models_validation.PGGenreAndFilmModel(**genre).dict()
                for genre in genres
            ]
        return []
