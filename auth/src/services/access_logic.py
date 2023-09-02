from typing import Annotated

from fastapi import Header
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth.schemas.entity import SingleRole

from auth.src.models.entity import Role, User, UserProfile
from auth.src.services import token_logic, user_logic


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
    return True if role_name == 'administrator' else False


async def view_roles(authorization: Annotated[str, Header()], db: AsyncSession) -> dict:
    result = await token_logic.get_token_authorization(authorization)
    if result.get('error'):
        return result
    access_token = result.get('token')
    user_id = await token_logic.get_user_id_by_token(access_token)
    if await check_user_is_admin(user_id, db):
        query = select(Role.name, Role.description)
        result = await db.execute(query)
        roles = result.fetchall()
        return {
            'success': [
                {'name': name, 'description': description} for name, description in roles
            ]
        }
    return {'access_error': 'Отсутствуют необходимые права доступа.'}


async def change_role(
    role_id: str, new_role_data: SingleRole,
    authorization: Annotated[str, Header()], db: AsyncSession
) -> dict:
    result = await token_logic.get_token_authorization(authorization)
    if result.get('error'):
        return result
    access_token = result.get('token')
    user_id = await token_logic.get_user_id_by_token(access_token)
    if await check_user_is_admin(user_id, db):
        role_found = await get_role_by_id_or_return_false(role_id, db)
        if role_found:
            if new_role_data.name and new_role_data.name != '':
                role_found.name = new_role_data.name
            if new_role_data.description and new_role_data.description != '':
                role_found.description = new_role_data.description
            await db.commit()
            return {
                'success': {
                    'name': new_role_data.name if (
                        new_role_data.name and new_role_data.name != ''
                    ) else role_found.name,
                    'description': new_role_data.description if (
                        new_role_data.description and new_role_data.description != ''
                    ) else role_found.description
                }
            }
        return {'not_found_error': 'Роль не найдена.'}
    return {'access_error': 'Отсутствуют необходимые права доступа.'}


async def get_role_by_id_or_return_false(id: str, db: AsyncSession) -> Role | bool:
    try:
        query = select(Role).where(Role.id == id)
        result = await db.execute(query)
        role = result.scalar_one_or_none()
        return role if role else False
    except DBAPIError:
        return False


async def delete_role(
    role_id: str, authorization: Annotated[str, Header()], db: AsyncSession
) -> dict:
    result = await token_logic.get_token_authorization(authorization)
    if result.get('error'):
        return result
    access_token = result.get('token')
    user_id = await token_logic.get_user_id_by_token(access_token)
    if await check_user_is_admin(user_id, db):
        role_found = await get_role_by_id_or_return_false(role_id, db)
        if role_found:
            await db.delete(role_found)
            await db.commit()
            return {'success': "Роль успешно удалена."}
        return {'not_found_error': 'Роль не найдена.'}
    return {'access_error': 'Отсутствуют необходимые права доступа.'}


async def assign_role(
    id_of_user_to_be_assigned: str, role_name: str,
    authorization: Annotated[str, Header()], db: AsyncSession
) -> dict:
    result = await token_logic.get_token_authorization(authorization)
    if result.get('error'):
        return result
    access_token = result.get('token')
    user_id = await token_logic.get_user_id_by_token(access_token)
    if not await check_user_is_admin(user_id, db):
        return {'access_error': 'Отсутствуют необходимые права доступа.'}
    role_id: str = await get_role_id_by_name_or_return_false(role_name.name, db)
    if not role_id:
        return {'not_found_error': 'Роль не найдена.'}
    user_profile: UserProfile = await user_logic.get_user_profile_by_id_or_return_false(
        id_of_user_to_be_assigned, db
    )
    if not user_profile:
        return {'not_found_error': 'Пользователь не найден.'}
    user_profile.role_id = role_id
    if role_name.name in ('editor', 'administrator'):
        user_profile.is_staff = True
    if role_name.name in ('registered user'):
        user_profile.is_staff = False
    await db.commit()
    return {'success': f'Роль {role_name.name} успешно присвоена пользователю.'}
    

async def get_role_id_by_name_or_return_false(
    role_name: str, db: AsyncSession
) -> str | bool:
    query = select(Role.id).where(Role.name == role_name)
    result = await db.execute(query)
    role_id = result.scalar_one_or_none()
    return role_id if role_id else False
