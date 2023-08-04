from datetime import datetime
from uuid import UUID
from fastapi import HTTPException, Request
from redis.asyncio import client
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash
from auth.schemas.entity import Token, UserRegistration, UserLogin
from auth.src.models.entity import User, LoginHistory
from auth.src.services import token_logic
from auth.src.models.entity import User, Role, UserProfile


default_role_name: str = 'registered user'


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


async def login_user(
    request: Request,
    user: UserLogin,
    db: AsyncSession,
    cache: client.Redis
) -> tuple:
    if await check_credentials_correct(user.login, user.password, db):
        user_id = await get_user_id_by_login(user, db)
        user_id_as_string = str(user_id)
        access_token, refresh_token = await token_logic.generate_tokens(user_id_as_string)
        await token_logic.save_refresh_token_to_cache(user_id_as_string, refresh_token, cache)
        await save_login_data_to_db(request, user_id, db)
        success = "Вы вошли в свою учётную запись."
        headers = {
            'X-Access-Token': access_token,
            'X-Refresh-Token': refresh_token
        }
        return success, headers


async def check_credentials_correct(login: str, password: str, db: AsyncSession) -> bool:
    query_for_login = select(User.login).filter(User.login == login)
    result = await db.execute(query_for_login)
    if result.scalar_one_or_none():
        query_for_password = select(
            User.hashed_password
        ).filter(User.login == login)
        result = await db.execute(query_for_password)
        hashed_password = result.scalar_one()
        if check_password_hash(hashed_password, password):
            return True
    raise HTTPException(status_code=401, detail='Логин или пароль не верен.')


async def get_user_id_by_login(user: UserLogin, db: AsyncSession) -> UUID:
    query = select(User.id).filter(User.login == user.login)
    result = await db.execute(query)
    user_id = result.scalar_one()
    return user_id


async def save_login_data_to_db(
        request: Request, user_id: UUID, db: AsyncSession
) -> None:
    login_data = LoginHistory(
        user_id=user_id,
        user_agent=request.headers.get('User-Agent'),
        login_dt=datetime.now()
    )
    db.add(login_data)
    await db.commit()
    await db.refresh(login_data)


async def fill_in_user_profile_table(db: AsyncSession, user: User) -> None:
    query_for_default_role = select(Role.id).filter(Role.name == default_role_name)
    result = await db.execute(query_for_default_role)
    default_role_id = result.scalar_one_or_none()
    if default_role_id:
        user_profile_table = UserProfile.__table__
        insert_query = (
            insert(user_profile_table).values(user_id=user.id, role_id=default_role_id)
        )
        await db.execute(insert_query)
    await db.commit()


async def logout_user(tokens: Token, cache: client.Redis) -> str:
    await token_logic.add_invalid_access_token_to_cache(tokens.access_token, cache)
    user_id = await token_logic.get_user_id_by_token(tokens.access_token)
    await token_logic.delete_refresh_token_from_cache(cache, user_id)
    return 'Вы вышли из учётной записи.'
