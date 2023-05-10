from dotenv import load_dotenv
from pydantic import BaseSettings

from src.core import config


load_dotenv()


conf = config.Settings()


class PGSettings(BaseSettings):
    """Settings for PostgreSQL database.

    """
    # DB_NAME: str
    # DB_USER: str
    # DB_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_OPTIONS: str = '-c search_path=content'

    class Config:
        env_file = config.BASE_DIR / '.env'


class ESSettings(BaseSettings):
    """Settings for Elasticsearch database.

    """
    ES_SCHEME: str = conf.ELASTIC_PORT
    ES_HOST: str = conf.ELASTIC_HOST
    ES_PORT: int = conf.ELASTIC_PORT
    ES_INDEX: str
    ES_GENRE_INDEX: str
    ES_SCHEMA: str
    ES_GENRE_SCHEMA: str

    class Config:
        env_file = config.BASE_DIR / '.env'


class ETLSettings(BaseSettings):
    """Settings for ETL pipeline.

    """
    LIMIT: int | None = 100
    LOAD_PAUSE: float = 2.0
    STATE_FIELD: str = None
    STATE_FILE_NAME: str = 'storage.json'

    class Config:
        env_file = config.BASE_DIR / '.env'


pg_settings = PGSettings()
es_settings = ESSettings()
etl_settings = ETLSettings()
