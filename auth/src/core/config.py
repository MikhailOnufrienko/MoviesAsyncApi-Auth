from pydantic import BaseSettings, PostgresDsn, RedisDsn, Field



class Settings(BaseSettings):
    DATABASE_DSN: PostgresDsn
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


app_settings = Settings()
