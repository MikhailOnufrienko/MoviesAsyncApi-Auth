from typing import Annotated

from fastapi import Request, Response
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from auth.schemas.entity import UserRegistration
from auth.src.services import user_logic
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import client

from auth.src.db.postgres import get_postgres_session
from auth.src.db.redis import get_redis


router = APIRouter()

DB_SESSION_DEPEND = Annotated[AsyncSession, Depends(get_postgres_session)]

REDIS_DEPEND = Annotated[client.Redis, Depends(get_redis)]


@router.post('/register', status_code=201, summary='Регистрация нового пользователя')
async def register_user(user: UserRegistration, db: DB_SESSION_DEPEND) -> JSONResponse:
    """Возвращает уведомление об успешной регистрации."""
    success = await user_logic.create_user(user, db)
    return JSONResponse(content=success, status_code=201)


@router.post('/login', status_code=200)
async def login_user(request: Request, user: UserRegistration, db: AsyncSession = Depends(get_postgres_session)) -> Response:
    response = await user_logic.login_user(request, user, db)
    return response
