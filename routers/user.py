"""User routes implementation."""

from fastapi import (Form, Depends, APIRouter, status,
                     Request)
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from utils.responses.user import admin_user

from domain.token import get_sub_authentication
from domain.user import validate_user_exists
from models.user import UserDTO
from settings.infra import get_db_postgres
from settings.sys_logger import SysLog, TypeLog, SystemMessages, user_str
from utils.utils import Utils

router = APIRouter(tags=["Users"], prefix="/users")


@router.get("/v1/users")
async def get_all(
        auth_jwt: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db_postgres)):
    """Get all users."""
    auth_jwt.jwt_required()
    users = await UserDTO(session).get_all_user()

    msg = SystemMessages.all_data.value.format("get", "users")
    SysLog(__name__).show_log(TypeLog.info.value, msg)

    return users


@router.get("/v1/user-by-token")
async def user_by_token(
        request: Request,
        jwt_auth: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db_postgres)):
    """Get user detail by token."""
    jwt_auth.jwt_required()

    current_username = get_sub_authentication(request, jwt_auth)

    user_details = await UserDTO(session).get_by_username(current_username)

    if user_details is None:
        msg = f'Usuário não encontrado: {current_username}'
        SysLog(__name__).show_log(TypeLog.error.value, msg)
        raise Utils().api_exception('api012', status.HTTP_404_NOT_FOUND)

    return user_details


@router.get("/v1/user/{username}")
async def get_by_username(
        username: str,
        auth_jwt: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db_postgres)) -> dict:
    """Get by user."""
    auth_jwt.jwt_required()

    user = await UserDTO(session).get_by_username(username)

    if user is None:
        msg = SystemMessages.not_exists.value.format(
            user_str, "get", f"user/{username}")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        raise Utils().api_exception("api012", status.HTTP_400_BAD_REQUEST)

    msg = SystemMessages.requested.value.format(
        user_str, "o", "get", f"user/{username}")
    SysLog(__name__).show_log(TypeLog.info.value, msg)

    return user


@router.post("/v1/user", responses=admin_user.get("create_user"))
async def user_creation(
        username: str = Form(None),
        first_name: str = Form(None),
        last_name: str = Form(None),
        is_active: bool = Form(False),
        phone: str = Form(None),
        country: str = Form(None),
        auth_jwt: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db_postgres)
):
    """User creation."""
    auth_jwt.jwt_required()

    user = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "complete_name": f'{first_name} {last_name}',
        "is_active": is_active,
        "language": "pt",
        "phone": phone,
        "type_user": 0,
        "country": country,
    }

    await validate_user_exists(user, session, auth_jwt)

    return {"detail": "api024"}


@router.put("/v1/user/{username}", responses=admin_user.get("update_user"))
async def user_update(
        username: str,
        first_name: str = Form(None),
        last_name: str = Form(None),
        is_active: bool = Form(False),
        phone: str = Form(None),
        country: str = Form(None),
        auth_jwt: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db_postgres)):
    """User update."""
    auth_jwt.jwt_required()

    user_dto = UserDTO(session)
    user_data = await user_dto.get_by_username(username)

    user = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "complete_name": f'{first_name} {last_name}',
        "is_active": is_active,
        "phone": phone,
        "country": country,
    }

    if user_data is None:
        msg = SystemMessages.not_exists.value.format(
            user_str, "put", f"user/{username}")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        raise Utils().api_exception("api012", status.HTTP_404_NOT_FOUND)

    if user:
        await user_dto.update(user_data.id, user)
        msg = SystemMessages.updated.value.format(
            user_str, "put", f"user/{username}")
        SysLog(__name__).show_log(TypeLog.info.value, msg)

    del user_dto

    return {"detail": "api036"}
