"""User Temporarily Blocked model implementation."""

from datetime import datetime, timedelta

from osirisvalidator.exceptions import ValidationException
from sqlalchemy import Column, Integer, DateTime, ForeignKey, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import validates

from models.abstract import BaseModel
from utils.utils import Utils


class UserTemporarilyBlocked(BaseModel):
    """User Temporarily Blocked model."""

    __tablename__ = 'user_temporarily_blocked'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    blocked_until = Column(DateTime, nullable=False)
    type_block = Column(Integer, nullable=True)

    @validates('user_id')
    def validate_user_id(self, key, user_id):
        """User id field registration validations."""
        if isinstance(user_id, int) and user_id <= 0:
            raise ValidationException(
                user_id, "User id must be greater than zero.")
        return user_id


class UserTemporarilyBlockedDTO:
    """User Temporarily Blocked data transfer object."""

    def __init__(self, session: AsyncSession) -> None:
        """Class initialization."""
        self.session = session
        self.util = Utils()

    async def user_block(self, user_id: int) -> dict:
        """If user is already blocked."""
        now = datetime.utcnow()

        query = select(UserTemporarilyBlocked).where(
            and_(UserTemporarilyBlocked.user_id == user_id,
                 UserTemporarilyBlocked.blocked_until >= now))

        result = await self.session.execute(query)
        user_block = result.scalars().first()

        return user_block

    async def insert_block_user(self, user_id: int,
                                block_minutes: int,
                                type_block: int) -> None:
        """User lock entered.."""
        blocked_until = datetime.utcnow() + timedelta(
            minutes=block_minutes)

        user_temporarily_blocked = UserTemporarilyBlocked(
            user_id=user_id, blocked_until=blocked_until,
            type_block=type_block)

        await self.util.database_commit(self.session, user_temporarily_blocked)
