from pydantic import BaseSettings, PostgresDsn, RedisDsn, Field



class Settings(BaseSettings):
    SERVICE_NAME: str = 'auth'
    DATABASE_DSN: str = 'postgresql+asyncpg://postgres:ghast13@localhost:5432/'
    DB_HOST: str = '127.0.0.1'
    DB_PORT: int = 5432
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = 'ghast13'
    DB_NAME: str = 'auth'
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_settings = Settings()
