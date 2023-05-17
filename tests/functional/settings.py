from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200')
    es_index: str = 'movies'
    es_id_field: str = 'id'
    base_url: str = 'http://127.0.0.1:8000/api/v1'
    pytest_query_exist: str = 'PYTESTFILM'
    pytest_query_nonexist: str = 'NOTEXIST'


test_settings = TestSettings()
