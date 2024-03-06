"""Fastapi app events."""

import aioredis
from fastapi import FastAPI

from database.redis import redis_url
from settings.fastapi_limiter import FastAPILimiter


def fastapi_events(app: FastAPI):
    """Start services before you upload the system."""
    @app.on_event("startup")
    async def startup():
        """Creation of access limit to routes."""
        redis = await aioredis.from_url(redis_url)
        await FastAPILimiter.init(redis)
