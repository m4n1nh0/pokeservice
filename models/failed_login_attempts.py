"""Failed Login Attempts model implementation."""

from osirisvalidator.exceptions import ValidationException
from sqlalchemy import Column, Integer, Boolean, ForeignKey, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import validates
from sqlalchemy.sql.expression import func

from models.abstract import BaseModel
from utils.utils import Utils


class FailedLoginAttempts(BaseModel):
    """Failed Login Attempts model."""

    __tablename__ = 'failed_login_attempt'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    is_validated = Column(Boolean, default=False, nullable=False)

    @validates('user_id')
    def validate_user_id(self, key, user_id):
        """User id field registration validations."""
        if isinstance(user_id, int) and user_id <= 0:
            raise ValidationException(
                user_id, "User id must be greater than zero.")
        return user_id


class FailedLoginAttemptsDTO:
    """Failed Login Attempts data transfer object."""

    def __init__(self, session: AsyncSession) -> None:
        """Class initialization."""
        self.session = session
        self.utils = Utils()

    async def get_count(self, user_id: int) -> int:
        """Get how many wrong accesses the user had."""
        query = select(func.count(FailedLoginAttempts.id)).where(and_(
            FailedLoginAttempts.user_id == user_id,
            FailedLoginAttempts.is_validated.is_(False)
        ))

        result = await self.session.execute(query)

        return result.scalar()

    async def insert_count(self, user_id: int) -> None:
        """Insert counter of how many times user failed to login."""
        failed_login_attempt = FailedLoginAttempts(user_id=user_id)
        await self.utils.database_commit(self.session, failed_login_attempt)

    async def insert_as_validated(self, user_id: int) -> None:
        """Register user's last attempts."""
        query = select(FailedLoginAttempts).where(
            and_(FailedLoginAttempts.user_id == user_id,
                 FailedLoginAttempts.is_validated.is_(False)))

        result = await self.session.execute(query)

        attempts = result.scalars().all()

        for attempt in attempts:
            attempt.is_validated = True
            self.session.add(attempt)

        await self.session.commit()
