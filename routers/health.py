"""Liveness router check implementation."""

from fastapi import APIRouter

router = APIRouter(tags=['Health'])


@router.get('/v1/health')
async def get_health() -> dict:
    """Get all health for liveness."""
    return dict(status="OK")
