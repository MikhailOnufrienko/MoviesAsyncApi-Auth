from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):

    es_host: str = Field('http://127.0.0.1:9200')
    es_movie_index: str = 'movies'
    es_person_index: str = 'person_index'
    es_genre_index: str = 'genres'
    es_id_field: str = 'id'
    service_url: str = 'http://127.0.0.1:8000/api/v1'
    pytest_query_exist: str = 'PYTESTFILM'
    pytest_query_nonexist: str = 'NOTEXIST'


#     es_host: str = Field('http://localhost:9200/', env='ELASTIC_HOST')
#     es_genre_index: str = 'genres'
#     es_person_index: str = 'persons'
#     es_id_field: str = 'id'
#     es_index_mapping: dict = {}

#     redis_host: str = Field('redis://127.0.0.1:6379/', env='REDIS_HOST')
#     service_url: str = Field(
#         'http://127.0.0.1:8000/api/v1/', env='SERVICE_URL'
    )

#     es_host: str = Field('http://127.0.0.1:9200')
#     es_index: str = 'movies'
#     es_id_field: str = 'id'
#     base_url: str = 'http://127.0.0.1:8000/api/v1'
#     pytest_query_exist: str = 'PYTESTFILM'
#     pytest_query_nonexist: str = 'NOTEXIST'




test_settings = TestSettings()
