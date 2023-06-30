from fastapi import Response
from fastapi import APIRouter, Depends
from auth.schemas.entity import UserRegistration
from auth.src.services.user_logic import UserService
from sqlalchemy.ext.asyncio import AsyncSession

from auth.src.db.postgres import get_postgres_session


router = APIRouter()

route_prefix: str = '/api/v1/auth'

register_route = '/user/register'
login_route = '/user/login'
refresh_token_route = '/user/refresh'
logout_route = '/user/logout'
change_credentials_route = '/user/change_credentials'
login_history_route = '/user/login_history'



@router.post('/register', status_code=201)
async def register_user(user: UserRegistration, db: AsyncSession = Depends(get_postgres_session)) -> Response:
    response = await UserService.create_user(user, db)
    return response


@router.post('/login', status_code=200)
async def login_user(user: UserRegistration) -> Response:
    response = await UserService.login_user(user)
    return response
