"""Meteo schemas implementation."""

from pydantic import BaseModel


class MeteoSchema(BaseModel):
    """Meteo schema."""

    city: str | None = 'aracaju'
