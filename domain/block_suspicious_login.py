"""Block Suspicious Login domain implementation."""

from sqlalchemy.ext.asyncio import AsyncSession

from domain.block_login import BlockLogin
from models.failed_login_attempts import FailedLoginAttemptsDTO
from models.user import User
from models.user_temporarily_blocked import UserTemporarilyBlockedDTO


class BlockSuspiciousLogin(BlockLogin):
    """Blocking methods."""

    BLOCKED_MINUTES = 1440

    def __init__(self, user: User) -> None:
        """Start variables."""
        super().__init__(user)

    async def count_one_more_request(self, session: AsyncSession) -> None:
        """Counter of how many times user made a mistake."""
        await FailedLoginAttemptsDTO(session).insert_count(self.user.id)
        await self._block_if_necessary(session)

    async def _block_if_necessary(self, session: AsyncSession) -> None:
        """Block the user if there are too many attempts."""
        attempts = await FailedLoginAttemptsDTO(
            session).get_count(self.user.id)
        if attempts >= self.MAX_ATTEMPTS:
            await UserTemporarilyBlockedDTO(session).insert_block_user(
                self.user.id, self.BLOCKED_MINUTES, 2)

            await self.mark_last_attempts_as_validated(session)
