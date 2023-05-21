from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):

    es_host: str = Field('http://127.0.0.1:9200')
    redis_host: str = Field('redis://127.0.0.1:6379/', env='REDIS_HOST')
    service_url: str = Field(
        'http://127.0.0.1:8000/api/v1/', env='SERVICE_URL'
    )
    es_movie_index: str = 'movies'
    es_person_index: str = 'person_index'
    es_genre_index: str = 'genres'
    es_id_field: str = 'id'


test_settings = TestSettings()
