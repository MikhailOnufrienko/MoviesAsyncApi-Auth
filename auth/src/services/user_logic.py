from fastapi import HTTPException, Response
from pydantic import ValidationError
from sqlalchemy.exc import NoResultFound
from werkzeug.security import generate_password_hash
from auth.schemas.entity import UserRegistration
from auth.src.db.postgres import async_session
from auth.src.models.entity import User


class UserService:

    @staticmethod
    async def create_user(user: UserRegistration) -> Response:
        if await UserService.all_checks_passed(user):
            success_text = await UserService.save_user_to_database(user)
            return Response(content=success_text, status_code=201)

    @staticmethod
    async def all_checks_passed(user: UserRegistration) -> bool:
        if await UserLoginPasswordEmailChecks.check_login_exists(user.login):
            raise HTTPException(
                status_code=400,
                detail='Пользователь с таким логином уже зарегистрирован.'
            )
        if not await UserLoginPasswordEmailChecks.check_password_length_correct(user.password):
            raise HTTPException(
                status_code=400,
                detail='Пароль должен быть длиной от 8 до 50 символов.'
            )
        if not await UserLoginPasswordEmailChecks.check_email_correct(user.email):
            raise HTTPException(
                status_code=400,
                detail='Формат введённого email неверен.'
            )
        return True

    @staticmethod
    async def save_user_to_database(user: UserRegistration) -> str:
        async with async_session() as session:
            hashed_password = generate_password_hash(user.password)
            new_user = User(
                login=user.login,
                hashed_password=hashed_password,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email
            )
            await session.add(new_user)
            await session.commit()
            return "Вы успешно зарегистрировались."


class UserLoginPasswordEmailChecks:

    @staticmethod
    async def check_login_exists(login: str) -> bool:
        async with async_session() as session:
            try:
                query = session.query(User).filter(User.login == login)
                await query.one()
                return True
            except NoResultFound:
                return False
            
    @staticmethod
    async def check_password_length_correct(password: str) -> bool:
        try:
            UserRegistration(password=password)
        except ValidationError:
            return False
        return True
    
    @staticmethod
    async def check_email_correct(email: str | None) -> bool:
        try:
            UserRegistration(email=email)
        except ValidationError:
            return False
        return True