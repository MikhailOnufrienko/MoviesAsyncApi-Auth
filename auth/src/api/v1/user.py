from typing import Annotated

from fastapi import Request, APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from redis.asyncio import client
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas.entity import Token, UserLogin, UserRegistration
from auth.src.db.postgres import get_postgres_session
from auth.src.db.redis import get_redis
from auth.src.services import user_logic


router = APIRouter()

DB_SESSION_DEPEND = Annotated[AsyncSession, Depends(get_postgres_session)]

REDIS_DEPEND = Annotated[client.Redis, Depends(get_redis)]


@router.post('/register', status_code=201, summary='Регистрация нового пользователя')
async def register_user(user: UserRegistration, db: DB_SESSION_DEPEND) -> JSONResponse:
    """Возвращает уведомление об успешной регистрации."""
    success = await user_logic.create_user(user, db)
    return JSONResponse(content=success, status_code=201)


@router.post('/login', status_code=200, summary='Вход в учётную запись')
async def login_user(
    request: Request,
    user: UserLogin,
    db: DB_SESSION_DEPEND,
    cache: REDIS_DEPEND
) -> JSONResponse:
    """
    Возвращает строку с уведомлением об успешной аутентификации.
    Заголовки 'X-Access-Token' и 'X-Refresh-Token' содержат соответствующие токены.
    """
    success, headers = await user_logic.login_user(request, user, db, cache)
    return JSONResponse(content=success, headers=headers)


@router.post('/logout', status_code=200, summary='Выход из учётной записи.')
async def logout_user(
    tokens: Token,
    cache: REDIS_DEPEND
) -> JSONResponse:
    """
    Возвращает строку с уведомлением о выходе из учётной записи.
    """
    success = await user_logic.logout_user(tokens, cache)
    return JSONResponse(content=success)
