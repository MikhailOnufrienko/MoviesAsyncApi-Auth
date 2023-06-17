from fastapi import FastAPI
from src.db.postgres import create_database


app = FastAPI()


@app.on_event('startup')
async def startup():
    # Импорт моделей необходим для их автоматического создания
    from src.models.entity import User
    await create_database()