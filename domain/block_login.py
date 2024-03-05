"""Block Login domain implementation."""

from sqlalchemy.ext.asyncio import AsyncSession

from models.failed_login_attempts import FailedLoginAttemptsDTO
from models.user import User
from models.user_temporarily_blocked import UserTemporarilyBlockedDTO


class BlockLogin:
    """Blocking methods."""

    MAX_ATTEMPTS = 3
    BLOCKED_MINUTES = 30

    def __init__(self, user: User) -> None:
        """Start variables."""
        self.user = user

    async def is_user_blocked(self, session: AsyncSession) -> dict:
        """Inform the blocked user."""
        return await UserTemporarilyBlockedDTO(session).user_block(
            self.user.id)

    async def count_one_more_password_mistake(self,
                                              session: AsyncSession) -> None:
        """Counter of how many times user made a mistake."""
        await FailedLoginAttemptsDTO(session).insert_count(self.user.id)
        await self.block_if_necessary(session)

    async def mark_last_attempts_as_validated(self,
                                              session: AsyncSession) -> None:
        """Last login attempts."""
        await FailedLoginAttemptsDTO(
            session).insert_as_validated(self.user.id)

    async def block_if_necessary(self, session: AsyncSession) -> None:
        """Block the user if there are too many attempts."""
        attempts = await FailedLoginAttemptsDTO(session
                                                ).get_count(self.user.id)
        if attempts >= self.MAX_ATTEMPTS:
            await UserTemporarilyBlockedDTO(session).insert_block_user(
                self.user.id, self.BLOCKED_MINUTES, 1)

            await self.mark_last_attempts_as_validated(session)
