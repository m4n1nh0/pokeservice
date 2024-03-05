"""Token domain implementation."""

from datetime import timedelta

from cryptocode import encrypt, decrypt
from fastapi import Request
from fastapi_jwt_auth import AuthJWT

from database.redis import redis_conn
from models.user import User
from settings.infra import (FIRST_ACCESS_TOKEN_DAY,
                            ACCESS_TOKEN_EXPIRE_MINUTES,
                            SECRET_TOKEN)


async def create_token(user: User, auth_jwt: AuthJWT,
                       access: bool = True) -> str:
    """JWT token create to username."""
    jti_access = auth_jwt.get_raw_jwt()

    if jti_access is not None:
        redis_token(jti_access['jti'], ACCESS_TOKEN_EXPIRE_MINUTES)

    secret_user = encrypt(user.username, SECRET_TOKEN)

    subject = f"{secret_user}"

    if access:
        access_token = auth_jwt.create_access_token(subject=subject,
                                                    algorithm="HS256")
        data = f"Bearer {access_token}"
    else:
        refresh_token = auth_jwt.create_refresh_token(subject=subject,
                                                      algorithm="HS256")
        data = f"Bearer {refresh_token}"

    return data


def create_token_expires(user: User, auth_jwt: AuthJWT,
                         time_expire: timedelta = timedelta(
                             hours=FIRST_ACCESS_TOKEN_DAY)):
    """Create the first access token."""
    return auth_jwt.create_access_token(
        subject=encrypt(user.username, SECRET_TOKEN),
        algorithm="HS256",
        expires_time=time_expire,
    )


def get_sub_authentication(request: Request, auth_jwt: AuthJWT) -> str:
    """Get username from token."""
    token = request.headers["Authorization"].replace("Bearer ", "")

    decoded = auth_jwt.get_raw_jwt(token)

    secret_user = decoded["sub"]

    user_name = decrypt(secret_user, SECRET_TOKEN)

    return user_name


def get_sub_first_access(token, auth_jwt) -> int:
    """Get username from token."""
    decoded = auth_jwt.get_raw_jwt(token)

    return decoded["sub"]


def get_token(request: Request):
    """."""
    return request.headers["Authorization"].replace("Bearer ", "")


def redis_token(jti, time: int):
    """Redis token controller."""
    redis_conn.setex(jti, time, 'true')
    redis_conn.close()
