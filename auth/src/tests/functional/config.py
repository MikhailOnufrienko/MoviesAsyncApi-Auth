from pydantic import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class TestSettings(BaseSettings):
    SERVICE_NAME: str = 'auth'
    TEST_DB_HOST: str = '127.0.0.1'
    TEST_DB_PORT: int = 5433
    TEST_DB_USER: str
    TEST_DB_PASSWORD: str
    TEST_DB_NAME: str = 'auth_test'
    TEST_REDIS_HOST: str = '127.0.0.1'
    TEST_REDIS_PORT: int = 6379
    TEST_REDIS_DB: int = 1
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = TestSettings()
