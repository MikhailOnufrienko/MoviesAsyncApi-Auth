from pydantic import BaseSettings, PostgresDsn, RedisDsn, Field



class Settings(BaseSettings):
    SERVICE_NAME: str = 'auth'
    DB_HOST: str = '127.0.0.1'
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str = 'auth_database'
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_settings = Settings()
