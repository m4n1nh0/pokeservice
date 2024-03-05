"""Double Factor schemas implementation."""

from pydantic import BaseModel, EmailStr


class DoubleFactorValidate(BaseModel):
    """Double Factor schemas."""

    code: str
    digest: str

    class Config:
        """Reading data even not being dict."""

        orm_mode = True


class DoubleFactorResend(BaseModel):
    """Double Factor Resend Schema."""

    username: EmailStr


class DoubleFactorOTP(BaseModel):
    """Double Factor Activate schema."""

    username: str
    code: str

    class Config:
        """Reading data even not being dict."""

        orm_mode = True


class QrCodeOTP(BaseModel):
    """User schema."""

    jwt_token: str
    double_factor_type: int

    class Config:
        """Reading data even not being dict."""

        orm_mode = True
