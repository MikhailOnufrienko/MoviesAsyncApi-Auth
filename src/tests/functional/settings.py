from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):

    es_host: str = Field('http://elastic_search:9200')
    redis_host: str = Field('redis://redis:6379/')
    service_url: str = Field('http://fastapi:8000/api/v1/')
    es_movie_index: str = 'movies'
    es_person_index: str = 'persons'
    es_genre_index: str = 'genres'
    es_id_field: str = 'id'


test_settings = TestSettings()
