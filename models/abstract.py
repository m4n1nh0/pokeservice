"""Base model implementation."""

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

from database.postgres import Base


class BaseModel(Base):
    """Base model."""

    __abstract__ = True
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
