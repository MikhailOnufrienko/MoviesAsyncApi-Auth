from pathlib import Path
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    REDIS_HOST: str = Field('127.0.0.1', env='REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='REDIS_PORT')
    ELASTIC_SCHEME: str = Field('http', env='ELASTIC_SCHEME')
    ELASTIC_HOST: str = Field('127.0.0.1', env='ELASTIC_HOST')
    ELASTIC_PORT: int = Field(9200, env='ELASTIC_PORT')
    PROJECT_NAME: str = Field('movies', env='PROJECT_NAME')

    class Config:
        env_file = '.env'


settings = Settings()
