"""Login routes implementation."""

from uuid import uuid4

from cryptocode import encrypt
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from domain import double_factor
from domain.authentication import Authentication
from domain.send_email import SendEmail
from domain.token import (get_sub_authentication, create_token,
                          redis_token, create_token_expires)
from domain.user import get_url_and_email_template
from models.user import UserDTO
from schemas.login import (LoginSchema, LoginForgotPassSchema,
                           LoginResetPasswordSchema, LoginFirstSchema)
from settings.infra import LIMITER, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_TOKEN, get_db_postgres
from settings.sys_logger import SysLog, TypeLog
from utils.responses.login import response_login
from utils.utils import Utils

# Variable for creating the root login
router = APIRouter(tags=["Login"])


@router.post("/v1/login", dependencies=LIMITER,
             responses=response_login.get("login"))
async def login(user_login: LoginSchema,
                background_tasks: BackgroundTasks,
                auth: Authentication = Depends(),
                session: AsyncSession = Depends(get_db_postgres)) -> dict:
    """System access."""
    user_data = await auth.authenticate_user(
        user_login.username, user_login.password, session)

    if user_data.double_factor_type == 1:
        await double_factor.double_factor_send_by_email(
            session, user_data.id, user_data.username,
            str(uuid4().int)[:8], background_tasks)

    secret_data = {
        "secret_key": Utils().secret_key_generator(),
        "secret_data": f"{str(uuid4().int)[:8]}"
    }

    await UserDTO(session).update(user_data.id, secret_data)

    digest = encrypt(secret_data["secret_data"], secret_data["secret_key"])
    digest = encrypt(f"{digest}P0K{user_data.id}", SECRET_TOKEN)

    msg = (f"Login efetuado com sucesso pelo usuário {user_data.username}. "
           f"method=post route=/login")
    SysLog(__name__).show_log(TypeLog.info.value, msg)

    return {
        "detail": "api017",
        "double_factor_type": user_data.double_factor_type,
        "digest": digest
    }


@router.post("/v1/first-access", dependencies=LIMITER,
             responses=response_login.get("first_access"))
async def first_access(
        user: LoginFirstSchema,
        auth_jwt: AuthJWT = Depends(),
        auth: Authentication = Depends(),
        session: AsyncSession = Depends(get_db_postgres),) -> dict:
    """Token validator to authenticate other services."""
    if user.double_factor_type not in [1, 2]:
        msg = (
            f"Duplo fator {user.double_factor_type} não existe. "
            f"method=post route=/v1/first-access")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        raise Utils().api_exception("api112", status.HTTP_400_BAD_REQUEST)

    await auth.new_password(
        user.dict(), session, auth_jwt, "first-access")

    return {"detail": "api017"}


@router.post("/v1/reset-password", dependencies=LIMITER)
async def reset_password(
        user: LoginResetPasswordSchema,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_db_postgres),
        auth_jwt: AuthJWT = Depends()) -> dict:
    """Reset Password sending the JWT token by email."""
    user_data = await UserDTO(session).get_by_username(user.username)

    if not user_data:
        raise Utils().api_exception("api056", status.HTTP_200_OK)

    user_data.first_access_done = False

    await Utils().database_commit(session, user_data)
    template_email, url_reset_password = (
        get_url_and_email_template("reset_password"))

    body = {
        'token': create_token_expires(user_data, auth_jwt),
        "url_reset_password": url_reset_password
    }

    SendEmail('Esqueci Minha Senha',
              [user_data.username],
              template_email, body).sync_send_email(background_tasks)

    return {'detail': 'api056'}


@router.post("/v1/forgot-password", dependencies=LIMITER)
async def forgot_password(
        user: LoginForgotPassSchema,
        auth_jwt: AuthJWT = Depends(),
        auth: Authentication = Depends(),
        session: AsyncSession = Depends(get_db_postgres)) -> dict:
    """."""
    await auth.new_password(
        user.dict(), session, auth_jwt, "forgot-password")

    return {'detail': "api025"}


@router.post("/v1/refresh", dependencies=LIMITER,
             responses=response_login.get("refresh"))
async def refresh(request: Request, auth_jwt: AuthJWT = Depends(),
                  session: AsyncSession = Depends(get_db_postgres)) -> dict:
    """JWT token update."""
    auth_jwt.jwt_refresh_token_required()

    username = get_sub_authentication(request, auth_jwt)

    user_data = await UserDTO(session).get_by_username(username)

    new_access_token = await create_token(
        user=user_data, auth_jwt=auth_jwt)

    return {"create_new_token": True,
            "access_token": new_access_token}


@router.post("/v1/access_revoke", dependencies=LIMITER)
def access_revoke(auth_jwt: AuthJWT = Depends()) -> dict:
    """Token storage is done in REDIS set with the value true for revoked."""
    auth_jwt.jwt_required()
    jti_access = auth_jwt.get_raw_jwt()['jti']

    redis_token(jti_access, ACCESS_TOKEN_EXPIRE_MINUTES)

    return {"detail": "api055"}


@router.post("/v1/refresh_revoke", dependencies=LIMITER)
def refresh_revoke(auth_jwt: AuthJWT = Depends()) -> dict:
    """Token storage is done in REDIS set with the value true for revoked."""
    auth_jwt.jwt_refresh_token_required()

    jti_access = auth_jwt.get_raw_jwt()['jti']

    redis_token(jti_access, ACCESS_TOKEN_EXPIRE_MINUTES)

    return {"detail": "api055"}
