import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from auth.src.core.config import app_settings
from auth.src.db.redis import get_redis
from auth.src.db.postgres import get_postgres_session


app = FastAPI(
    title=app_settings.SERVICE_NAME,
    docs_url='/auth/api/openapi',
    openapi_url='/auth/api/openapi.json',
    default_response_class=ORJSONResponse
)


@app.on_event('startup')
async def startup() -> None:
    global redis, postgres
    redis = await get_redis()
    async for session in get_postgres_session():
        postgres = session


@app.on_event('shutdown')
async def shutdown() -> None:
    await redis.close()
    await postgres.close()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8001
    )