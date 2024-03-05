"""Double factor model implementation."""

from datetime import datetime, timedelta

from osirisvalidator.exceptions import ValidationException
from osirisvalidator.string import not_blank, not_empty, string_len
from sqlalchemy import (Column, Integer, String, DateTime,
                        Boolean, and_, update)
from sqlalchemy import (ForeignKey)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import validates

from models.abstract import BaseModel
from settings.infra import DOUBLE_FACTOR_EXPIRY_TIME_MINUTES
from utils.utils import Utils


class DoubleFactor(BaseModel):
    """Double Factor model."""

    __tablename__ = 'double_factor'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    code = Column(String(256), nullable=False)
    valid_until = Column(DateTime, nullable=False)
    code_confirmed = Column(Boolean, default=False, nullable=False)

    @validates('user_id')
    def validate_user_id(self, key, user_id):
        """User id field registration validations."""
        if isinstance(user_id, int) and user_id <= 0:
            raise ValidationException(
                user_id, 'User id must be greater than zero.')
        return user_id

    @validates('code')
    @string_len(field='code', min=1, max=8,
                message='Code must contain 8 characters')
    @not_blank(field='code', message='Code not blank')
    @not_empty(field='code', message='Code not empty')
    def validate_code(self, key, code):
        """Code field registration validations."""
        return code


class DoubleFactorDTO:
    """Double Factor data transfer object."""

    def __init__(self, session: AsyncSession) -> None:
        """Class initialization."""
        self.session = session
        self.utils = Utils()

    async def get_by_code(self, code: str) -> DoubleFactor:
        """Get user by code."""
        query = select(DoubleFactor).where(and_(DoubleFactor.code == code))
        result = await self.session.execute(query)
        return result.scalars().first()

    async def can_resend_code(self,
                              user_id: int) -> bool:
        """Return true if the user can resend code."""
        query = select(DoubleFactor).where(
            and_(DoubleFactor.user_id == user_id,
                 DoubleFactor.code_confirmed.is_(False))
        )

        result = await self.session.execute(query)
        double_factor = result.scalars().first()
        if not double_factor:
            return False

        now = datetime.utcnow()
        if now <= double_factor.valid_until:
            return False
        if now >= double_factor.valid_until + timedelta(seconds=30):
            return True

    async def get_validate_code(self, code: str) -> DoubleFactor:
        """Get the code and verify if it was not used."""
        query = select(DoubleFactor).where(and_(
            DoubleFactor.code_confirmed.is_(False),
            DoubleFactor.code == code
        ))
        result = await self.session.execute(query)
        return result.scalars().first()

    async def insert(self, code: str, user_id: int) -> datetime:
        """Double Factor creation."""
        valid_until = datetime.utcnow() + timedelta(
            minutes=DOUBLE_FACTOR_EXPIRY_TIME_MINUTES)

        double_factor = DoubleFactor(
            user_id=user_id,
            code=code,
            valid_until=valid_until,
        )
        await self.utils.database_commit(self.session, double_factor)

        return valid_until

    async def update(self, user_id):
        """Attributing truth to ancient values."""
        query = update(DoubleFactor).where(
            and_(DoubleFactor.user_id == user_id,
                 DoubleFactor.code_confirmed.is_(False))
        ).values(code_confirmed=True)

        await self.session.execute(query)
