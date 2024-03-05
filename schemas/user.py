"""User schemas implementation."""

from pydantic import BaseModel, EmailStr


class UserInSchema(BaseModel):
    """User Out Schema."""

    country: str
    first_name: str
    is_active: bool = True
    last_name: str
    language: str
    group_id: int
    phone: str | None = None
    type_user: int
    username: EmailStr


class UserUpdateSchema(BaseModel):
    """User Out Schema."""

    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    group_id: int
    phone: str | None = None
    country: str | None = None
    language: str | None = None
