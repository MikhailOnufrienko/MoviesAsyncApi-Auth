from fastapi import HTTPException, Response
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash
from auth.schemas.entity import UserRegistration
from auth.src.db.postgres import get_postgres_session
from auth.src.models.entity import User


class UserService:

    @staticmethod
    async def create_user(user: UserRegistration, db: AsyncSession) -> Response:
        if not await UserService.check_login_exists(user.login) and not await UserService.check_email_exists(user.email):
            success_text = await UserService.save_user_to_database(user, db)
            return Response(content=success_text, status_code=201)

    @staticmethod
    async def check_login_exists(login: str) -> bool:
        async for session in get_postgres_session():
            query_for_login = select(User).filter(User.login == login)
            result = await session.execute(query_for_login)
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail='Пользователь с таким логином уже зарегистрирован.')
            return False
        
    @staticmethod
    async def check_email_exists(email: str | None) -> bool:
        if email:
            async for session in get_postgres_session():
                query_for_email = select(User).filter(User.email == email)
                result = await session.execute(query_for_email)
                if result.scalar_one_or_none():
                    raise HTTPException(status_code=400, detail='Пользователь с таким email уже зарегистрирован.')
            return False

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
    
    @staticmethod
    async def login_user(login: str, password: str, db: AsyncSession) -> Response:
        pass
