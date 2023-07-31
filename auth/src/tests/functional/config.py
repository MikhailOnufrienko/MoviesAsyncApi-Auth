from pydantic import BaseSettings
from dotenv import load_dotenv


load_dotenv()


class TestSettings(BaseSettings):
    SERVICE_NAME: str = 'auth'
    DB_HOST: str = '127.0.0.1'
    DB_PORT: int = 5433
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str = 'auth_test'
    
    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'


settings = TestSettings()
