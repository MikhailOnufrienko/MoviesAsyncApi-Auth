from typing import Annotated

from fastapi import Header, Request, APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from redis.asyncio import client
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas.entity import ChangeCredentials, Token, UserLogin, UserRegistration
from auth.src.db.postgres import get_postgres_session
from auth.src.db.redis import get_redis
from auth.src.services import token_logic, user_logic


router = APIRouter()

DB_SESSION_DEPEND = Annotated[AsyncSession, Depends(get_postgres_session)]

REDIS_DEPEND = Annotated[client.Redis, Depends(get_redis)]


@router.post('/register', status_code=201, summary='Регистрация нового пользователя')
async def register_user(user: UserRegistration, db: DB_SESSION_DEPEND) -> JSONResponse:
    """Возвращает уведомление об успешной регистрации."""
    result = await user_logic.create_user(user, db)
    if result.get('error'):
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result, status_code=201)


@router.post('/login', status_code=200, summary='Вход в учётную запись')
async def login_user(
    request: Request,
    user: UserLogin,
    db: DB_SESSION_DEPEND,
    cache: REDIS_DEPEND
) -> JSONResponse:
    """
    Возвращает уведомление об успешной аутентификации.
    Заголовки 'X-Access-Token' и 'X-Refresh-Token' содержат соответствующие токены.
    """
    result = await user_logic.login_user(request, user, db, cache)
    if result.get('error'):
        return JSONResponse(content=result, status_code=401)
    return JSONResponse(content=result['success'], headers=result['headers'], status_code=200)


@router.post('/logout', status_code=200, summary='Выход из учётной записи.')
async def logout(
    authorization: Annotated[str, Header()],
    cache: REDIS_DEPEND
) -> JSONResponse:
    """
    Возвращает уведомление о выходе из учётной записи или ошибку авторизации.
    """
    result = await user_logic.logout_user(authorization, cache)
    if result.get('error'):
        return JSONResponse(content=result, status_code=401)
    return JSONResponse(content=result, status_code=200)


@router.post(
    '/{user_id}/refresh',
    response_model=Token,
    status_code=201,
    summary='Запрос на обновление токенов.'
)
async def refresh_tokens(user_id: str, tokens: Token, cache: REDIS_DEPEND) -> Token:
    """
    Возвращает новые токены с параметрами:
    - **access_token**: новый токен для авторизации
    - **refresh_token**: новый токен для обновления токена авторизации

    """
    result = await token_logic.refresh_tokens(
        user_id, tokens.access_token, tokens.refresh_token, cache
    )
    if result.get('error'):
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result, status_code=201)

@router.patch(
        '/change_credentials',
        status_code=200,
        summary='Запрос на изменение логина и/или пароля.'
)
async def change_credentials(
    credentials: ChangeCredentials,
    authorization: Annotated[str, Header()],
    db: DB_SESSION_DEPEND,
    cache: REDIS_DEPEND
) -> JSONResponse:
    """
    Возвращает уведомление об успешном изменении учётных данных либо ошибку."
    """
    result = await user_logic.change_credentials(credentials, authorization, db, cache)
    if result.get('pass_error'):
        return JSONResponse(content=result, status_code=401)
    if result.get('login_error'):
        return JSONResponse(content=result, status_code=409)
    return JSONResponse(content=result, status_code=200)
