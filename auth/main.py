import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.core.config import app_settings
from src.db.redis import get_redis


app = FastAPI(
    title=app_settings.SERVICE_NAME,
    docs_url='/auth/api/openapi',
    openapi_url='/auth/api/openapi.json',
    default_response_class=ORJSONResponse
)


@app.on_event('startup')
async def startup() -> None:
    global redis
    redis = await get_redis()


@app.on_event('shutdown')
async def shutdown() -> None:
    await redis.close()


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8001
    )