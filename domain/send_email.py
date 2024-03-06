"""Send Email domain implementation."""

from pathlib import Path

from fastapi import BackgroundTasks

from fastapi_mail import ConnectionConfig, MessageSchema, FastMail
from prettyconf import config

from settings.sys_logger import SysLog, TypeLog


class SendEmail:
    """Sending email from the system."""

    def __init__(self, subject: str, email: list,
                 template_name: str, template_body: dict) -> None:
        """Class initialization."""
        self.conf = self.get_mail_connection_config()
        self.fastapi_mail = FastMail(self.conf)
        self.template_name = template_name
        self.message = MessageSchema(
            subject=subject,
            recipients=email,
            template_body=template_body,
            subtype='html',
        )

    def sync_send_email(self, task: BackgroundTasks) -> None:
        """To send synchronous email."""
        task.add_task(self.fastapi_mail.send_message,
                      self.message,
                      template_name=self.template_name)

    async def async_send_email(self) -> None:
        """To send asynchronous email."""
        await self.fastapi_mail.send_message(self.message,
                                             template_name=self.template_name)

    @staticmethod
    def get_mail_connection_config():
        """Return Connection instance to send mail with FastAPI library."""
        try:
            return ConnectionConfig(
                MAIL_USERNAME=config('MAIL_USERNAME'),
                MAIL_PASSWORD=config('MAIL_PASSWORD'),
                MAIL_FROM=config('MAIL_FROM', default='no-replay@ish-labs.com'),
                MAIL_PORT=config('MAIL_PORT', default=587),
                MAIL_SERVER=config('MAIL_SERVER'),
                MAIL_FROM_NAME='RaidStorm',
                MAIL_TLS=True,
                MAIL_SSL=False,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True,
                TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates',
            )
        except Exception as e:
            msg = f"Erro ao conectar o Mail Sender: {e}"
            SysLog(__name__).show_log(TypeLog.error.value, msg)
