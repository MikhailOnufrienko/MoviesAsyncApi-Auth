from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID
from fastapi import Header, Request
from redis.asyncio import client
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash, check_password_hash
from auth.schemas.entity import (ChangeCredentials, LoginHistoryResponse,
                                 LoginHistorySingleRecord, UserRegistration, UserLogin)
from auth.src.models.entity import User, LoginHistory
from auth.src.services import token_logic
from auth.src.models.entity import User, Role, UserProfile


default_role_name: str = 'registered user'


async def create_user(user: UserRegistration, db: AsyncSession) -> str:
    result = await check_login_not_exists(user.login, db)
    if isinstance(result, dict):
        return result
    result = await check_email_not_exists(user.email, db)
    if isinstance(result, dict):
        return result
    await save_user_to_database(user, db)
    return {'success': 'Вы успешно зарегистрировались.'}


async def check_login_not_exists(login: str, db: AsyncSession) -> bool | dict:
    query = select(User.login).filter(User.login == login)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        return {'login_error': f'Пользователь с логином {login} уже зарегистрирован.'}
    return True
    

async def check_email_not_exists(email: str, db: AsyncSession) -> bool | dict:
    query = select(User.email).filter(User.email == email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        return {'email_error': f'Пользователь с email {email} уже зарегистрирован.'}
    return True


async def save_user_to_database(user: UserRegistration, db: AsyncSession) -> None:
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


async def login_user(
    request: Request,
    user: UserLogin,
    db: AsyncSession,
    cache: client.Redis
) -> dict:
    if await check_credentials_correct(user.login, user.password, db):
        user_id = await get_user_id_by_login(user, db)
        user_id_as_string = str(user_id)
        access_token, refresh_token = await token_logic.generate_tokens(user_id_as_string)
        await token_logic.save_refresh_token_to_cache(
            user_id_as_string, refresh_token, cache
        )
        await save_login_data_to_db(request, user_id, db)
        success = {'success': 'Вы вошли в свою учётную запись.'}
        headers = {
            'X-Access-Token': access_token,
            'X-Refresh-Token': refresh_token
        }
        return {'success': success, 'headers': headers}
    return {'error': 'Логин или пароль не верен.'}


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
    return False


async def check_password_correct_and_return_id_or_error(
    access_token: str, password: str, db: AsyncSession
) -> dict:
    user_id = await token_logic.get_user_id_by_token(access_token)
    user_login = await get_user_login(user_id, db)
    query_for_password = select(
        User.hashed_password
    ).filter(User.login == user_login)
    result = await db.execute(query_for_password)
    hashed_password = result.scalar_one()
    if check_password_hash(hashed_password, password):
        return {'user_id': user_id, 'user_login': user_login}
    return {'pass_error': 'Неверный старый пароль.'}


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


async def logout_user(
    authorization: Annotated[str, Header()], cache: client.Redis
) -> dict:
    result = await token_logic.get_token_authorization(authorization)
    if result.get('error'):
        return result
    access_token = result.get('token')
    await token_logic.add_invalid_access_token_to_cache(access_token, cache)
    user_id = await token_logic.get_user_id_by_token(access_token)
    await token_logic.delete_refresh_token_from_cache(cache, user_id)
    return {'success': 'Вы вышли из учётной записи.'}


async def change_credentials(
    credentials: ChangeCredentials,
    authorization: Annotated[str, Header()],
    db: AsyncSession,
    cache: client.Redis
) -> dict:
    result = await token_logic.get_token_authorization(authorization)
    if result.get('error'):
        return result
    access_token = result.get('token')
    result =  await check_password_correct_and_return_id_or_error(
        access_token, credentials.old_password, db
    )
    if result.get('pass_error'):
        return result
    user_id = result.get('user_id')
    current_user_login = result.get('user_login')
    if (credentials.new_login
        and credentials.new_login != ''
        and credentials.new_login != current_user_login):
        result = await check_login_not_exists(credentials.new_login, db)
        if isinstance(result, dict):
            return result
    result = await save_changed_credentials(credentials, user_id, db)
    return result


async def get_user_login(user_id: str, db: AsyncSession) -> str:
    query = select(User.login).filter(User.id == user_id)
    result = await db.execute(query)
    login = result.scalar_one()
    return login


async def save_changed_credentials(
    credentials: ChangeCredentials, user_id: str, db: AsyncSession
) -> dict:
    query = select(User).filter(User.id == user_id)
    user = await db.execute(query)
    user = user.scalar_one_or_none()
    if credentials.new_password:
        hashed_password = generate_password_hash(credentials.new_password)
        user.hashed_password = hashed_password
    if credentials.new_login:
            user.login = credentials.new_login
    await db.commit()
    return {'success': 'Данные успешно изменены.'}


async def get_login_history(
    authorization: Annotated[str, Header()],
    db: AsyncSession
) -> dict:
    result = await token_logic.get_token_authorization(authorization)
    if result.get('error'):
        return result
    access_token = result.get('token')
    user_id = await token_logic.get_user_id_by_token(access_token)
    query = select(LoginHistory).where(LoginHistory.user_id == user_id)
    login_history = await db.scalars(query)
    return {'success': [{
            'user_agent': record.user_agent,
            'login_dt': record.login_dt.isoformat()
    } for record in login_history]
    }


async def get_user_profile_by_id_or_return_false(
    id: str, db: AsyncSession
) -> Optional[UserProfile]:
    try:
        query = select(UserProfile).where(UserProfile.user_id == id)
        result = await db.execute(query)
        user_profile = result.scalar_one_or_none()
        return user_profile
    except Exception:
        return None
