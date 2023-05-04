import logging
from datetime import datetime

import pydantic
from psycopg2.extensions import connection as pg_connection

from utils.logging_settings import setup_logging
from utils.pydantic_schemas import PersonInfo

setup_logging()


class PostgresExtractor:

    def __init__(self, connection: pg_connection, block_size: int) -> None:
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.cursor.execute('SET search_path TO content;')
        self.cursor.arraysize = block_size

    def extract_data(
            self, start_time: datetime,
            extract_time: datetime, excluded_ids: list
    ) -> list:
        """Extracting person data from PostgreSQL."""

        query = f"""
            SELECT p.id, p.full_name
            FROM person p
            WHERE p.modified > '{extract_time}'
        """

        if excluded_ids:
            query += f"""
                AND (
                    p.id not in '{excluded_ids}' OR
                    MAX(p.modified) > '{start_time}'
                )
            """

        query += 'ORDER BY p.modified DESC;'

        self.cursor = self.connection.cursor()
        self.cursor.execute(query)

        while True:
            data = self.cursor.fetchmany()

            if not data:
                break

            model_data = []

            for row in data:
                try:
                    PersonInfo(**row)
                except pydantic.ValidationError as exc:
                    logging.exception('Validation Error: %s', exc)

                model_data.append(dict(row))

                excluded_ids.append(row['id'])

            yield model_data

        self.cursor.close()
