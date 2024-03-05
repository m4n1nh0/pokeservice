"""User domain implementation."""

from typing import Any
from uuid import uuid4

from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from passlib.handlers.pbkdf2 import pbkdf2_sha512
from sqlalchemy.ext.asyncio import AsyncSession

from domain.send_email import SendEmail
from domain.token import create_token_expires
from models.user import UserDTO
from settings.infra import URL_EMAIL
from settings.sys_logger import SysLog, TypeLog, SystemMessages, user_str


async def validate_user_exists(user: dict, session: AsyncSession,
                               auth_jwt: AuthJWT = Depends()) -> None:
    """."""
    user_dto = UserDTO(session)

    user_exists = await user_dto.get_by_username(user["username"])

    user["complete_name"] = f"{user['first_name']} {user['last_name']}"

    if user_exists is not None:
        await user_dto.update(user_exists.id, {
            "edited_by_system": user["created_by_system"],
            "edited_by_user": user["create_by_user"]
        })

        msg = SystemMessages.exists.value.format(
            user_str, user['username'], "post", "user")
        SysLog(__name__).show_log(TypeLog.info.value, msg)
    else:
        user["password"] = pbkdf2_sha512.hash(
            f"P0K@451!#{str(uuid4().int)[:6]}")

        await user_dto.insert(user)

        user_data = await user_dto.get_by_username(user["username"])

        template_email, url_first_access = get_url_and_email_template(
            "first_access")

        body = {'token': create_token_expires(user_data, auth_jwt),
                'url_first_access': url_first_access}

        send_mail = SendEmail('Primeiro Acesso',
                              [user["username"]], template_email, body)

        await send_mail.async_send_email()

        msg = SystemMessages.recorded.value.format(
            user_str, user["username"], "post", "user")
        SysLog(__name__).show_log(TypeLog.info.value, msg)

    del user_dto


def get_url_and_email_template(template: str) -> Any:
    """Get the email template and the url for the project.

    :param template: Get an existing template name from the folder.
    :return: Project Url: Direct to manager or RaidStorm and
             Template_email: Html existing in the template folder.
    """

    template_email = f"/mail/poke/{template}.html"
    project_url = URL_EMAIL

    return template_email, project_url
