"""Double factor routes implementation."""

from uuid import uuid4

import pyotp
from cryptocode import decrypt
from fastapi import Depends, APIRouter, status, BackgroundTasks, Request
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from domain import double_factor
from domain.block_suspicious_login import BlockSuspiciousLogin
from domain.token import (create_token, get_sub_first_access)
from models.user import UserDTO
from schemas.double_factor import (DoubleFactorValidate, DoubleFactorResend,
                                   QrCodeOTP)
from settings.infra import get_db_postgres, LIMITER, SECRET_TOKEN
from settings.sys_logger import SystemMessages, SysLog, TypeLog, user_str
from utils.responses.double_factor import response_dbf
from utils.utils import Utils

router = APIRouter(
    tags=['Double Factor'],
    responses={401: {'User': 'Not Authorized'}})


@router.post('/v1/double-factor/validate', dependencies=LIMITER,
             responses=response_dbf.get("validate"))
async def double_factor_validate(
        dfv_data: DoubleFactorValidate,
        auth_jwt: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db_postgres)) -> dict:
    """Validate Double Factor code."""
    digest_decrypt = decrypt(dfv_data.digest, SECRET_TOKEN)
    utils = Utils()
    if "P0K" not in digest_decrypt:
        msg = (f"Digest {digest_decrypt} está incorreto. "
               f"method=post route=/v1/double-factor/validate")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        raise utils.api_exception('api007', status.HTTP_400_BAD_REQUEST)

    digest, user_id = digest_decrypt.split("P0K")
    user_data = await UserDTO(session).get_by_id(int(user_id))
    route = "double-factor/validate"

    if not user_data:
        msg = SystemMessages.not_exists.value.format(
            user_str, "post", route)
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        raise utils.api_exception('api007', status.HTTP_400_BAD_REQUEST)

    digest = decrypt(digest, user_data.secret_key)

    if digest != user_data.secret_data:
        raise utils.api_exception('api007', status.HTTP_400_BAD_REQUEST)

    block_suspicious = BlockSuspiciousLogin(user_data)
    block_is_user = await block_suspicious.is_user_blocked(session)
    if block_is_user:
        block_is_user = block_is_user.__dict__
        if block_is_user["type_block"] == 1:
            msg = SystemMessages.blocked.value.format(
                user_data.username, "post", route)
            SysLog(__name__).show_log(TypeLog.warning.value, msg)
            raise utils.api_exception("api008", status.HTTP_401_UNAUTHORIZED)
        else:
            msg = SystemMessages.blocked_24_hours.value.format(
                user_data.username, "post", route)
            SysLog(__name__).show_log(TypeLog.warning.value, msg)
            raise utils.api_exception("api107", status.HTTP_401_UNAUTHORIZED)

    if user_data.double_factor_type == 1:
        await double_factor.validate(session, dfv_data.code,
                                     user_data, block_suspicious)
    elif user_data.double_factor_type == 2:
        totp = pyotp.TOTP(user_data.otp_secret)
        if not totp.verify(dfv_data.code):
            msg = (f"Usuário {user_data.username} digitou código "
                   f"otp incorreto. method=post route={route}")
            SysLog(__name__).show_log(TypeLog.info.value, msg)

            await block_suspicious.count_one_more_request(session)
            raise utils.api_exception('api013', status.HTTP_400_BAD_REQUEST)

    data = {"detail": "api017", "access_token": await create_token(
        user=user_data, auth_jwt=auth_jwt),
            "refresh_token": await create_token(
        user=user_data, auth_jwt=auth_jwt, access=False)}

    msg = (f"Token operador {user_data.username} criado. "
           f"method=post route={route}")
    SysLog(__name__).show_log(TypeLog.info.value, msg)

    await block_suspicious.mark_last_attempts_as_validated(session)

    await UserDTO(session).update(
        user_data.id, {"secret_data": None, "secret_key": None})

    return data


@router.post("/v1/double-factor/resend", dependencies=LIMITER,
             responses=response_dbf.get("resend"))
async def double_factor_resend_code(
        dfr_data: DoubleFactorResend,
        background_tasks: BackgroundTasks,
        session: AsyncSession = Depends(get_db_postgres)) -> dict:
    """Resend code to user's mail."""
    user_data = await UserDTO(session).get_by_username(dfr_data.username)

    if not user_data:
        msg = SystemMessages.not_exists.value.format(
            user_str, "post", "double-factor/resend")
        SysLog(__name__).show_log(TypeLog.info.value, msg)

        raise Utils().api_exception('api106', status.HTTP_400_BAD_REQUEST)

    code = str(uuid4().int)[:8]

    await double_factor.resend_code(session, user_data,
                                    code, background_tasks)

    await BlockSuspiciousLogin(user_data).mark_last_attempts_as_validated(
        session)

    return {'detail': 'api021'}


@router.post("/v1/double-factor/generate_qr_code", dependencies=LIMITER)
async def double_factor_generate_qr_code(
        qrcode: QrCodeOTP,
        auth_jwt: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_db_postgres)) -> dict:
    """Generate a new otp secret to logged user."""
    utils = Utils()
    user_token = get_sub_first_access(qrcode.jwt_token, auth_jwt)
    username = decrypt(user_token, SECRET_TOKEN)
    user_data = await UserDTO(session).get_by_username(username)
    route = "double-factor/generate_qr_code"
    if not user_data:
        msg = SystemMessages.not_exists.value.format(
            user_str, "post", route)
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        raise utils.api_exception('api012', status.HTTP_400_BAD_REQUEST)

    block_suspicious = BlockSuspiciousLogin(user_data)
    block_is_user = await block_suspicious.is_user_blocked(session)
    if block_is_user:
        block_is_user = block_is_user.__dict__
        if block_is_user["type_block"] == 1:
            msg = SystemMessages.blocked.value.format(
                user_data.username, "post", route)
            SysLog(__name__).show_log(TypeLog.warning.value, msg)
            raise utils.api_exception("api008", status.HTTP_401_UNAUTHORIZED)
        else:
            msg = SystemMessages.blocked_24_hours.value.format(
                user_data.username, "post", route)
            SysLog(__name__).show_log(TypeLog.warning.value, msg)
            raise utils.api_exception("api107", status.HTTP_401_UNAUTHORIZED)

    data = {}
    if qrcode.double_factor_type == 2:
        await block_suspicious.mark_last_attempts_as_validated(session)
        qr_code = await double_factor.create_qr_code(user_data, session)

        data['username'] = user_data.username
        data['otp_secret'] = user_data.otp_secret
        data['qr_code'] = qr_code

        msg = (f"QR Code OTP do usuário {user_data.username} criado. "
               f"method=post route=/v1/{route}")
        SysLog(__name__).show_log(TypeLog.info.value, msg)

    else:
        msg = (f"Tipo verificação duplo-fator incorreto do usuário "
               f"{user_data.username}. method=post route=/v1/{route}")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        await block_suspicious.count_one_more_request(session)
        data = utils.api_exception("api068", status.HTTP_400_BAD_REQUEST)

    return data
