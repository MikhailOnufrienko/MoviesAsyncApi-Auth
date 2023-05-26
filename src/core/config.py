from pathlib import Path
from logging import config as logging_config

from pydantic import BaseSettings, Field

from src.core.logger import LOGGING


logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(env='PROJECT_NAME')

    REDIS_HOST: str = Field(env='REDIS_HOST')
    REDIS_PORT: int = Field(env='REDIS_PORT')

    ELASTIC_SCHEME: str = Field(env='ELASTIC_SCHEME')
    ELASTIC_HOST: str = Field(env='ELASTIC_HOST')
    ELASTIC_PORT: int = Field(env='ELASTIC_PORT')

    ES_MOVIE_INDEX: str
    ES_GENRE_INDEX: str
    ES_PERSON_INDEX: str

    REDIS_CACHE_EXPIRES_IN_SECONDS = 60 * 5

    class Config:
        env_file = BASE_DIR / '.env'


settings = Settings()
