"""Double factor domain implementation."""

from datetime import datetime
from uuid import uuid4

import pyotp
from fastapi import status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from domain.block_suspicious_login import BlockSuspiciousLogin
from domain.send_email import SendEmail
from domain.user import get_url_and_email_template
from models.double_factor import DoubleFactorDTO
from models.user import User
from settings.sys_logger import SysLog, TypeLog
from utils.utils import Utils


async def validate(session: AsyncSession, code: str, user: User,
                   block_suspicious: BlockSuspiciousLogin) -> None:
    """Code validator."""
    double_factor = await DoubleFactorDTO(session).get_validate_code(code)
    utils = Utils()
    if not double_factor:
        msg = (f"Usuário {user.username} digitou código por email incorreto. "
               f"method=post route=/v1/double-factor/validate")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        await block_suspicious.count_one_more_request(session)
        raise utils.api_exception("api013", status.HTTP_400_BAD_REQUEST)

    if double_factor.valid_until < datetime.utcnow():
        msg = (f"Token do usuário {user.username} expirou. "
               f"method=post route=/v1/double-factor/validate")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
        await block_suspicious.count_one_more_request(session)
        raise utils.api_exception("api014", status.HTTP_412_PRECONDITION_FAILED)

    double_factor.code_confirmed = True
    await utils.database_commit(session, double_factor)


async def resend_code(session, user, code,
                      background_tasks: BackgroundTasks) -> str:
    """Resend the double factor code."""
    double_factor_dto = DoubleFactorDTO(session)
    can_resend_code = await double_factor_dto.can_resend_code(user.id)
    utils = Utils()
    if not can_resend_code:
        msg = (f"Falha no envio do código para {user.username}. "
               f"method=post route=/v1/double-factor/resend")
        SysLog(__name__).show_log(TypeLog.info.value, msg)

        await BlockSuspiciousLogin(user).count_one_more_request(
            session)
        raise utils.api_exception('api106', status.HTTP_400_BAD_REQUEST)

    return await double_factor_send_by_email(
        session, user.id, user.username, code, background_tasks)


async def double_factor_send_by_email(
        session: AsyncSession, user_id: int,
        email: str, code: str,
        background_tasks: BackgroundTasks) -> str:
    """Send and verification of the double factor code by email."""
    double_factor_dto = DoubleFactorDTO(session)
    await double_factor_dto.update(user_id)

    exists = False
    while not exists:
        exists = await double_factor_dto.get_by_code(code)
        if exists:
            code = str(uuid4().int)[:8]
        else:
            await double_factor_dto.insert(code, user_id)
            exists = True

    template_email, _ = get_url_and_email_template("double_factor_code")
    body = {'code': code}

    SendEmail('Código de Verificação', [email],
              template_email, body).sync_send_email(background_tasks)

    msg = f"Código {code} enviado para {email}"
    SysLog(__name__).show_log(TypeLog.info.value, msg)

    return code


async def create_qr_code(logged_user, session) -> str:
    """Generate a new otp secret to logged user."""
    utils = Utils()
    if not logged_user.otp_secret:
        otp_secret = pyotp.random_base32()
        logged_user.otp_secret = otp_secret
        await utils.database_commit(session, logged_user)

        msg = (f"Gerando o OTP Secret do usuário {logged_user.username}."
               f"method=post route=/v1/double-factor/generate_qr_code")
        SysLog(__name__).show_log(TypeLog.info.value, msg)

    qr_code = pyotp.totp.TOTP(logged_user.otp_secret).provisioning_uri(
        name=logged_user.username,
        issuer_name='PokeService'
    )

    return qr_code
