from pydantic import BaseSettings, PostgresDsn, RedisDsn, Field



class Settings(BaseSettings):
    SERVICE_NAME: str = 'auth'
#    DATABASE_DSN: PostgresDsn
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_settings = Settings()
