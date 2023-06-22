from fastapi import Response
from auth.main import app
from auth.schemas.entity import UserRegistration
from auth.src.services.user_logic import UserService


route_prefix: str = '/api/v1/auth'

register_route = '/user/register'
login_route = '/user/login'
refresh_token_route = '/user/refresh'
logout_route = '/user/logout'
change_credentials_route = '/user/change_credentials'
login_history_route = '/user/login_history'



@app.post('/user/register')
async def register_user(user: UserRegistration) -> Response:
    response = await UserService.create_user(user)
    return response
