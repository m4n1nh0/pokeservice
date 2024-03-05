"""Postgresql database implementation."""

from prettyconf import config
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

# DATABASE CONFIGURATION
POSTGRES_URL = config("POSTGRES_URL")

async_engine = create_async_engine(
    POSTGRES_URL,
    poolclass=NullPool,
    future=True)

SessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


def news_connections(db_string: str):
    """Get new database connections from other microservices."""
    return create_async_engine(
        db_string,
        poolclass=NullPool,
        future=True)
