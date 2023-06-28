from fastapi import HTTPException, Response
from pydantic import ValidationError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash
from auth.schemas.entity import UserRegistration
from auth.src.db.postgres import get_postgres_session
from auth.src.models.entity import User


class UserService:

    @staticmethod
    async def create_user(user: UserRegistration, db: AsyncSession) -> Response:
        if await UserService.all_checks_passed(user):
            success_text = await UserService.save_user_to_database(user, db)
            return Response(content=success_text, status_code=201)

    @staticmethod
    async def all_checks_passed(user: UserRegistration) -> bool:
        if await UserLoginPasswordEmailChecks.check_login_exists(user.login):
            raise HTTPException(
                status_code=400,
                detail='Пользователь с таким логином уже зарегистрирован.'
            )
        if not await UserLoginPasswordEmailChecks.check_password_length_correct(user):
            raise HTTPException(
                status_code=400,
                detail='Пароль должен быть длиной от 8 до 50 символов'
            )
        if not await UserLoginPasswordEmailChecks.check_email_correct(user):
            raise HTTPException(
                status_code=400,
                detail='Формат введённого email неверен.'
            )
        return True

    @staticmethod
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
        await db.refresh(new_user)
        return "Вы успешно зарегистрировались."


class UserLoginPasswordEmailChecks:
    
    @staticmethod
    async def check_login_exists(login: str) -> bool:
        async for session in get_postgres_session():
            query = select(User).filter(User.login == login)
            result = await session.execute(query)
            if result.scalar_one_or_none():
                return True
            return False
            
    @staticmethod
    async def check_password_length_correct(user: UserRegistration) -> bool:
        try:
            UserRegistration(login=user.login, password=user.password)
        except ValidationError:
            return False
        return True
    
    @staticmethod
    async def check_email_correct(user: UserRegistration | None) -> bool:
        try:
            UserRegistration(login=user.login, password=user.password, email=user.email)
        except ValidationError:
            return False
        return True
