from datetime import datetime

import pydantic
from psycopg2.extensions import connection as pg_connection

from utils.pydantic_schemas import PersonInfo


class PostgresExtractor:

    def __init__(self, connection: pg_connection, block_size: int) -> None:
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.cursor.execute('SET search_path TO content;')
        self.cursor.arraysize = 10
    
    def extract_data(self,
            # start_time: datetime,
            # extract_time: datetime, excluded_ids: list
    ) -> list:
        """Extracting person data from PostgreSQL."""

        query = f"""
            SELECT p.id, p.full_name
            FROM person p
        """

        # if excluded_ids:
        #     query += f"""
        #         AND (
        #             p.id not in '{excluded_ids}' OR
        #             MAX(p.modified) > '{start_time}'
        #         )
        #     """
        
        query += 'ORDER BY id DESC;'

        self.cursor.execute(query)

        while True:
            data = self.cursor.fetchmany()

            if not data:
                break

            model_data = []

            for row in data:
                try:
                    PersonInfo(**row)
                    # model_data.append(PersonInfo(**row))
                    # model_data.append(row)
                except pydantic.ValidationError as exc:
                    pass # logging in future

                model_data.append(dict(row))
            
                # excluded_ids.append(row['id'])
            
            yield model_data
        
        self.cursor.close()
