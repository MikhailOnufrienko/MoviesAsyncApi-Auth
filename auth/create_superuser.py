from typing import Annotated, Optional

import typer
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from auth.src.core.config import app_settings
from src.models.entity import Role, User, UserProfile


DATABASE_DSN: str = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'.format(
    user=app_settings.DB_USER,
    password=app_settings.DB_PASSWORD,
    host=app_settings.DB_HOST,
    port=app_settings.DB_PORT,
    name=app_settings.DB_NAME
)


engine = create_engine(DATABASE_DSN)


def create_superuser(
    username: Annotated[str, typer.Option(prompt='Имя суперпользователя')],
    password: Annotated[str, typer.Option(
        prompt='Пароль суперпользователя', confirmation_prompt=True, hide_input=True
    )],
    email: Annotated[Optional[str], typer.Option(
        prompt='Имейл суперпользователя (не обязательно)'
    )] = None
):
    '''Create a superuser with all available permissions.'''
    with Session(engine) as db_session:
        result = check_login_not_exists(username, db_session)
        if isinstance(result, dict):
            typer.echo(f'Пользователь с именем {username} уже существует.')
            return
        if email:
            result = check_email_not_exists(email, db_session)
            if isinstance(result, dict):
                typer.echo(f'Пользователь с имейлом {email} уже существует.')
                return        
        hashed_password = generate_password_hash(password)
        superuser = User(login=username, hashed_password=hashed_password, email=email)
        db_session.add(superuser)
        db_session.commit()
        fill_in_user_profile_table(db_session, superuser)
        typer.echo(f'Суперпользователь {username} успешно создан.')


def check_login_not_exists(login: str, db: Session) -> bool | dict:
    query = select(User.login).filter(User.login == login)
    result = db.execute(query)
    if result.scalar_one_or_none():
        return {'login_error': f'Пользователь с логином {login} уже зарегистрирован.'}
    return True
    

def check_email_not_exists(email: str, db: Session) -> bool | dict:
    query = select(User.email).filter(User.email == email)
    result = db.execute(query)
    if result.scalar_one_or_none():
        return {'email_error': f'Пользователь с email {email} уже зарегистрирован.'}
    return True


def fill_in_user_profile_table(db: Session, user: User) -> None:
    query_for_superuser_role = select(Role.id).filter(Role.name == 'administrator')
    result = db.execute(query_for_superuser_role)
    role_id = result.scalar_one_or_none()
    if role_id:
        user_profile_table = UserProfile.__table__
        insert_query = (
            insert(user_profile_table).values(user_id=user.id, role_id=role_id)
        )
        db.execute(insert_query)
    db.commit()


if __name__ == '__main__':
    typer.run(create_superuser)
