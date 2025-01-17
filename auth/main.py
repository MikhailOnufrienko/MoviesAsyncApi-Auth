import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError

from auth.src.core.config import app_settings
from auth.src.db.redis import get_redis
from auth.src.db.postgres import get_postgres_session
from auth.src.api.v1 import role, user


app = FastAPI(
    title=app_settings.SERVICE_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.errors()},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
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


app.include_router(user.router, prefix='/api/v1/auth/user', tags=['user'])
app.include_router(role.router, prefix='/api/v1/auth/access', tags=['access'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='127.0.0.1',
        port=8001, 
        reload=True
    )
