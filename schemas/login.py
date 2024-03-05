"""Login schemas implementation."""

from pydantic import BaseModel, EmailStr


class LoginSchema(BaseModel):
    """Login schema."""

    username: EmailStr
    password: str


class LoginFirstSchema(BaseModel):
    """First access schema."""

    jwt_token: str
    password: str
    password_confirmation: str
    double_factor_type: int = 1

    class Config:
        """Reading data even not being dict."""

        orm_mode = True


class LoginForgotPassSchema(BaseModel):
    """Forgot Password schema."""

    jwt_token: str
    password: str
    password_confirmation: str


class LoginResetPasswordSchema(BaseModel):
    """Reset Password schema."""

    username: EmailStr
