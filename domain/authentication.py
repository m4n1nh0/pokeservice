"""Authentication domain implementation."""

import datetime
import re

from cryptocode import decrypt
from fastapi import status
from fastapi_jwt_auth import AuthJWT
from passlib.hash import pbkdf2_sha512
from sqlalchemy.ext.asyncio import AsyncSession

from domain.block_login import BlockLogin
from domain.block_suspicious_login import BlockSuspiciousLogin
from domain.token import get_sub_first_access, redis_token
from models.user import UserDTO, User

from settings.infra import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_TOKEN
from settings.sys_logger import SysLog, TypeLog, SystemMessages

from utils.utils import Utils


class Authentication:
    """Authentication methods."""

    def __init__(self):  # Variable for creating the password hash.
        """Start variables."""
        self.pwd_pbkdf2 = pbkdf2_sha512
        self.utils = Utils()

    def get_password_hash(self, password) -> str:
        """Hash application to create the user's password."""
        # Validation for creating a secure password.
        if len(password) < 8:
            raise self.utils.api_exception("api001",
                                           status.HTTP_400_BAD_REQUEST)
        if not any(x.isdigit() for x in password):
            raise self.utils.api_exception("api002",
                                           status.HTTP_400_BAD_REQUEST)
        if not any(x.isupper() for x in password):
            raise self.utils.api_exception("api003",
                                           status.HTTP_400_BAD_REQUEST)
        if not any(x.islower() for x in password):
            raise self.utils.api_exception("api004",
                                           status.HTTP_400_BAD_REQUEST)
        if re.match(r'^\w+$', password):
            raise self.utils.api_exception("api005",
                                           status.HTTP_400_BAD_REQUEST)

        return self.pwd_pbkdf2.hash(password)

    def verify_password(self, password, hashed_password):
        """Check if the password entered by the user is correct."""
        return self.pwd_pbkdf2.verify(password, hashed_password)

    async def authenticate_user(self,
                                username: str,
                                password: str,
                                session: AsyncSession) -> User:
        """Verification of the user's existence in the registry."""
        user = await UserDTO(session).get_by_username(username)

        # Message returned that the user does not exist in the system.
        if not user:
            msg = (f"Usuário {username} não encontrado. "
                   f"method=post route=/login")
            SysLog(__name__).show_log(TypeLog.info.value, msg)

            raise self.utils.api_exception("api006",
                                           status.HTTP_401_UNAUTHORIZED)

        block_suspicious = BlockSuspiciousLogin(user)

        if not user.first_access_done:
            await block_suspicious.count_one_more_request(session)
            msg = (f"Usuário {username} não fez primeiro acesso. "
                   f"method=post route=/login")
            SysLog(__name__).show_log(TypeLog.info.value, msg)

            raise self.utils.api_exception("api007",
                                           status.HTTP_401_UNAUTHORIZED)

        block_login = BlockLogin(user)
        block_is_user = await block_login.is_user_blocked(session)
        if block_is_user:
            block_is_user = block_is_user.__dict__
            if block_is_user["type_block"] == 1:

                msg = SystemMessages.blocked.value.format(
                    username, "post", "login")
                SysLog(__name__).show_log(TypeLog.warning.value, msg)

                raise self.utils.api_exception("api008",
                                               status.HTTP_401_UNAUTHORIZED)
            else:
                msg = SystemMessages.blocked_24_hours.value.format(
                    username, "post", "login")
                SysLog(__name__).show_log(TypeLog.warning.value, msg)
                raise self.utils.api_exception("api107",
                                               status.HTTP_401_UNAUTHORIZED)

        if not self.verify_password(password, user.password):
            msg = (f"Usuário {username} digitou senha errada. "
                   f"method=post route=/login")
            SysLog(__name__).show_log(TypeLog.warning.value, msg)
            await block_login.count_one_more_password_mistake(session)
            raise self.utils.api_exception("api006",
                                           status.HTTP_401_UNAUTHORIZED)

        user.last_login = datetime.datetime.now()

        if not user.updated_at:
            user.updated_at = None

        if user.double_factor_type == 2:
            user.otp_authentication = True

        await self.utils.database_commit(session, user)

        await block_login.mark_last_attempts_as_validated(session)

        return user

    async def new_password(self, user: dict,
                           session: AsyncSession,
                           auth_jwt: AuthJWT,
                           log_url: str) -> None:
        """."""
        user_token = get_sub_first_access(user["jwt_token"], auth_jwt)
        username = decrypt(user_token, SECRET_TOKEN)
        user_dto = UserDTO(session)

        user_data = await user_dto.get_by_username(username)
        if not user_data:
            msg = SystemMessages.not_exists.value.format(
                "Usuário", "post", log_url)
            SysLog(__name__).show_log(TypeLog.info.value, msg)

            raise self.utils.api_exception("api007",
                                           status.HTTP_401_UNAUTHORIZED)

        if user_data.first_access_done is True:
            msg = (f"Usuário {user_data.username} já fez primeiro acesso. "
                   f"method=post route={log_url}")
            SysLog(__name__).show_log(TypeLog.info.value, msg)

            raise self.utils.api_exception(
                "api010", status.HTTP_412_PRECONDITION_FAILED)

        if user["password"] != user["password_confirmation"]:
            msg = (f"A senha do usuário {user_data.username}  não conferem. "
                   f"method=post route={log_url}")
            SysLog(__name__).show_log(TypeLog.info.value, msg)

            raise self.utils.api_exception(
                "api009", status.HTTP_400_BAD_REQUEST)

        user_data.password = self.get_password_hash(user["password"])

        if "double_factor_type" in user:
            user_data.double_factor_type = user["double_factor_type"]

        user_data.first_access_done = True

        jti = auth_jwt.get_raw_jwt(user["jwt_token"])['jti']
        redis_token(jti, ACCESS_TOKEN_EXPIRE_MINUTES)

        await self.utils.database_commit(session, user_data)

        msg = (f"Senha do usuário {user_data.username} "
               f"atualizada com sucesso. "
               f"method=post route={log_url}")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
