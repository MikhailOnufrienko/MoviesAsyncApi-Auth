from typing import Annotated

from fastapi import Header, Request, APIRouter
from fastapi.responses import JSONResponse

from auth.schemas.entity import AllRolesResponse, RoleName, SingleRole
from auth.src.db.postgres import DB_SESSION_DEPEND
from auth.src.db.redis import REDIS_DEPEND
from auth.src.services import access_logic, token_logic, user_logic


router = APIRouter()


@router.post('/role', status_code=201, summary='Создание новой роли')
async def create_role(
    role: SingleRole, authorization: Annotated[str, Header()], db: DB_SESSION_DEPEND
) -> JSONResponse:
    """Возвращает уведомление об успешном создании новой роли или ошибку."""
    result = await access_logic.create_role(role, authorization, db)
    if result.get('error'):
        return JSONResponse(content=result, status_code=401)
    if result.get('access_error'):
        return JSONResponse(content=result, status_code=403)
    if result.get('success'):
        return JSONResponse(content=result, status_code=201)


@router.get(
    '/role', status_code=200,
    response_model=AllRolesResponse, summary='Просмотр всех ролей'
)
async def role_list(
    authorization: Annotated[str, Header()], db: DB_SESSION_DEPEND
) -> JSONResponse:
    """Возвращает список всех ролей или ошибку."""
    result = await access_logic.view_roles(authorization, db)
    if result.get('error'):
        return JSONResponse(content=result, status_code=401)
    if result.get('access_error'):
        return JSONResponse(content=result, status_code=403)
    if result.get('success'):
        return JSONResponse(content=result, status_code=200)


@router.put(
    '/role/{role_id}', status_code=200,
    response_model=SingleRole, summary='Изменение роли по идентификатору'
)
async def change_role(
    role_id: str, new_role_data: SingleRole,
    authorization: Annotated[str, Header()], db: DB_SESSION_DEPEND
) -> JSONResponse:
    """Возвращает информацию об изменённой роли или ошибку."""
    result = await access_logic.change_role(role_id, new_role_data, authorization, db)
    if result.get('error'):
        return JSONResponse(content=result, status_code=401)
    if result.get('access_error'):
        return JSONResponse(content=result, status_code=403)
    if result.get('not_found_error'):
        return JSONResponse(content=result, status_code=404)
    if result.get('success'):
        return JSONResponse(content=result, status_code=200)


@router.delete(
    '/role/{role_id}', status_code=200, summary='Удаление роли по идентификатору'
)
async def delete_role(
    role_id: str, authorization: Annotated[str, Header()], db: DB_SESSION_DEPEND
) -> JSONResponse:
    """Возвращает уведомление об удалении роли или ошибку."""
    result = await access_logic.delete_role(role_id, authorization, db)
    if result.get('error'):
        return JSONResponse(content=result, status_code=401)
    if result.get('access_error'):
        return JSONResponse(content=result, status_code=403)
    if result.get('not_found_error'):
        return JSONResponse(content=result, status_code=404)
    if result.get('success'):
        return JSONResponse(content=result, status_code=200)


@router.patch(
    '/user/{user_id}/role', status_code=200,
    summary='Назначение роли пользователю по идентификатору.'
)
async def assign_role(
    user_id: str, role_name: RoleName,
    authorization: Annotated[str, Header()], db: DB_SESSION_DEPEND
) -> JSONResponse:
    """Возвращает уведомление о назначении пользователю роли или ошибку."""
    result = await access_logic.assign_role(user_id, role_name, authorization, db)
    if result.get('error'):
        return JSONResponse(content=result, status_code=401)
    if result.get('access_error'):
        return JSONResponse(content=result, status_code=403)
    if result.get('not_found_error'):
        return JSONResponse(content=result, status_code=404)
    if result.get('success'):
        return JSONResponse(content=result, status_code=200)
