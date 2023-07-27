from datetime import datetime
import json
from uuid import UUID
from fastapi import HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash
from auth.schemas.entity import UserRegistration, UserLogin
from auth.src.db.postgres import get_postgres_session
from auth.src.models.entity import User, LoginHistory
from auth.src.services.utils import generate_access_token, generate_refresh_token, save_refresh_token_to_cache
from auth.src.core.config import app_settings
from auth.src.services.utils import fill_in_user_profile_table


async def create_user(user: UserRegistration, db: AsyncSession) -> str:
    if (await check_login_not_exists(user.login, db)
        and await check_email_not_exists(user.email, db)):
        success = await save_user_to_database(user, db)
        return success


async def check_login_not_exists(login: str, db: AsyncSession) -> bool:
    query = select(User.login).filter(User.login == login)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail='Пользователь с таким логином уже зарегистрирован.'
        )
    return True
    

async def check_email_not_exists(email: str, db: AsyncSession) -> bool:
    query = select(User.email).filter(User.email == email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail='Пользователь с таким email уже зарегистрирован.'
        )
    return True


async def save_user_to_database(user: UserRegistration, db: AsyncSession) -> str:
    hashed_password = generate_password_hash(user.password)
    new_user = User(
        login=user.login,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email
    )
    db.add(new_user)
    await db.commit()
    await fill_in_user_profile_table(db, new_user)
    return "Вы успешно зарегистрировались."


async def login_user(request: Request, user: UserLogin, db: AsyncSession) -> Response:
    if await check_credentials_correct(user.login, user.password):
        access_token, refresh_token = await generate_tokens(user)
        user_id = await get_user_id(user)
        await save_refresh_token_to_cache(user_id, refresh_token)
        await save_login_data_to_db(request, user_id, db)
        content = json.dumps({
            'user_id': user_id,
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        response = Response(status_code=200, content=content)
        response.headers['Content-Type'] = 'application/json'
        return response
    raise HTTPException(status_code=401, detail='Логин или пароль не верен.')


async def check_credentials_correct(login: str, password: str) -> bool:
    query_for_user = select(User).filter(User.login == login)
    async for session in get_postgres_session():
        result = await session.execute(query_for_user)
        if result.scalar_one_or_none():
            query_for_password = select(User.hashed_password).filter(User.login == login)
            result = await session.execute(query_for_password)
            hashed_password = result.scalar_one()
            if check_password_hash(hashed_password, password):
                return True
        return False
    

async def generate_tokens(user: UserLogin) -> tuple[str]:
    username = {'sub': user.login}
    access_token = await generate_access_token(username, app_settings.ACCESS_TOKEN_EXPIRES_IN)
    refresh_token = await generate_refresh_token(username, app_settings.REFRESH_TOKEN_EXPIRES_IN)
    return access_token, refresh_token


async def get_user_id(user: UserLogin) -> str:
    query_for_id = select(User.id).filter(User.login == user.login)
    async for session in get_postgres_session():
        result = await session.execute(query_for_id)
        return str(result.scalar_one())


async def save_login_data_to_db(request: Request, user_id: UUID, db: AsyncSession):
    login_data = LoginHistory(
        user_id=user_id,
        user_agent=request.headers.get('User-Agent'),
        login_dt=datetime.now()
    )
    db.add(login_data)
    await db.commit()
    await db.refresh(login_data)
