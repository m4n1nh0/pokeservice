"""User model implementation."""

import enum
from typing import Sequence

from sqlalchemy import (Boolean, Column, Integer, String, DateTime,
                        select, update, and_)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from sqlalchemy.sql import func
from sqlalchemy_utils import EmailType

from models.abstract import BaseModel
from utils.utils import Utils


class DoubleFactorType(enum.Enum):
    """Double factor type enum class."""

    email = 1
    security_app = 2


class User(BaseModel):
    """User model."""

    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(EmailType, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    last_login = Column(DateTime, default=func.now())
    first_access_done = Column(Boolean, default=False)
    otp_secret = Column(String(50), nullable=True)
    otp_authentication = Column(Boolean, default=False)
    double_factor_type = Column(Integer, default=DoubleFactorType.email.value)
    complete_name = Column(String, nullable=True, index=True)
    language = Column(String(10), nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    phone = Column(String, nullable=True)
    country = Column(String, nullable=True)


class UserDTO():
    """User data transfer object."""

    def __init__(self, session: AsyncSession) -> None:
        """Class initialization."""
        self.session = session
        self.utils = Utils()

    async def get_all_user(self) -> Sequence[User]:
        """Get all users."""
        query = select(User)
        users = (await self.session.execute(query)).scalars().unique().all()

        return users

    async def get_by_id(self, pk: int) -> User:
        """Get user by id."""
        query = select(User).where(and_(User.id == pk))
        result = (await self.session.execute(query)).scalars().first()

        return result

    async def get_by_username(self, username: str) -> User:
        """Get user by username."""
        query = select(User)
        query = query.options(
            load_only(User.complete_name,
                      User.username,
                      User.language,
                      User.country,
                      User.first_name,
                      User.last_name,
                      User.phone,
                      User.first_access_done,
                      User.last_login,
                      User.otp_authentication,
                      User.password,
                      User.created_at,
                      User.updated_at,
                      User.double_factor_type,
                      User.is_active)
        ).where(and_(User.username == username))

        result = (await self.session.execute(query)).scalars().first()

        return result

    async def insert(self, user: dict) -> None:
        """User creation."""
        user_created = User(**user)

        await self.utils.database_commit(self.session, user_created)

    async def update(self, pk: int, user: dict) -> None:
        """User update."""
        query = update(User).where(and_(User.id == pk)).values(**user)
        await self.session.execute(query)
        await self.session.commit()
