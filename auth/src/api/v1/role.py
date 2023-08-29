from typing import Annotated

from fastapi import Header, Request, APIRouter
from fastapi.responses import JSONResponse

from auth.schemas.entity import NewRole
from auth.src.db.postgres import DB_SESSION_DEPEND
from auth.src.db.redis import REDIS_DEPEND
from auth.src.services import access_logic, token_logic, user_logic


router = APIRouter()


@router.post('/role', status_code=201, summary='Создание новой роли')
async def create_role(
    role: NewRole, authorization: Annotated[str, Header()], db: DB_SESSION_DEPEND
) -> JSONResponse:
    """Возвращает уведомление об успешном создании новой роли или ошибку."""
    result = await access_logic.create_role(role, authorization, db)
    if result.get('error'):
        return JSONResponse(content=result, status_code=401)
    if result.get('access_error'):
        return JSONResponse(content=result, status_code=403)
    if result.get('success'):
        return JSONResponse(content=result, status_code=201)
