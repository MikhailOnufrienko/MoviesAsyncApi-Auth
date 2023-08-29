from typing import Annotated

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auth.src.models.entity import Role, UserProfile
from auth.src.services import token_logic


async def create_role(
        role: Role, authorization: Annotated[str, Header()], db: AsyncSession
    ) -> dict:
    result = await token_logic.get_token_authorization(authorization)
    if result.get('error'):
        return result
    access_token = result.get('token')
    user_id = await token_logic.get_user_id_by_token(access_token)
    if await check_user_is_admin(user_id, db):
        new_role = Role(
            name=role.name,
            description=role.description
        )
        db.add(new_role)
        await db.commit()
        return {'success': 'Роль успешно создана.'}
    return {'access_error': 'Отсутствуют необходимые права доступа.'}

async def check_user_is_admin(user_id: str, db: AsyncSession) -> bool:
    query = select(Role.name).where(
        Role.id == UserProfile.role_id
        ).where(UserProfile.user_id == user_id)
    role_name = await db.scalar(query)
    return True if role_name == 'admin' else False
