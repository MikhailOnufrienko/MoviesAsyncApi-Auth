from typing import Annotated

from fastapi import Header, Request, APIRouter
from fastapi.responses import JSONResponse

from auth.schemas.entity import *
from auth.src.db.postgres import DB_SESSION_DEPEND
from auth.src.db.redis import REDIS_DEPEND
from auth.src.services import token_logic, user_logic


router = APIRouter()


@router.post('/role', status_code=201, summary='Создание новой роли')
async def create_role():
    """Возвращает уведомление об успешном создании новой роли или ошибку."""
    
