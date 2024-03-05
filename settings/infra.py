from pathlib import Path
from fastapi import Depends
from prettyconf import config

from database.postgres import SessionLocal as PostgresAsync
from settings.fastapi_limiter import RateLimiter
from utils.utils import Utils

# Variables > SECURITY
SECRET_KEY = config("SECRET_KEY", default=Utils().secret_key_generator())
SECRET_TOKEN = config("SECRET_TOKEN", default=Utils().secret_key_generator())

# Variables > DATABASE
POSTGRES_URL = config("POSTGRES_URL", default=None)

# Variables > EXPIRATION SETTINGS
DOUBLE_FACTOR_EXPIRY_TIME_MINUTES = int(
    config("DOUBLE_FACTOR_EXPIRY_TIME_MINUTES", default="2"))

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    config("ACCESS_TOKEN_EXPIRE_MINUTES", default="60"))

FIRST_ACCESS_TOKEN_DAY = int(
    config("FIRST_ACCESS_TOKEN_DAY", default="120"))

# Variables > SYSTEM SETTINGS

OPENAPI_URL = config("OPEN_API_URL", default=None)
RE_DOC_URL = config("REDOC", default=None)
DOCS_URL = config("DOCS", default=None)

# Variables > URLS ACCESS VALIDATIONS
REQUEST_ORIGIN = config("REQUEST_ORIGIN")

if "," in REQUEST_ORIGIN:
    REQUEST_ORIGIN = REQUEST_ORIGIN.split(",")
else:
    REQUEST_ORIGIN = [REQUEST_ORIGIN]

ALLOW_ORIGINS = config("ALLOW_ORIGINS", default=None)

if "," in ALLOW_ORIGINS:
    ALLOW_ORIGINS = ALLOW_ORIGINS.split(",")
else:
    ALLOW_ORIGINS = [ALLOW_ORIGINS]

AMBIENT_HOST = config("AMBIENT_HOST", default=None)
if "," in AMBIENT_HOST:
    AMBIENT_HOST = AMBIENT_HOST.split(',')
else:
    AMBIENT_HOST = [AMBIENT_HOST]

URL_EMAIL = config("URL_EMAIL", default=None)

# RUNNING ENVIRONMENT
AMBIENT = config("AMBIENT")

# ROUTE CLICK LIMITER
LIMITER = [Depends(RateLimiter(times=5, seconds=3))]

ROOT_DIR = Path(__file__).parent.parent


# Functions
async def get_db_postgres():
    """Dependency function that yields db sessions."""
    async with PostgresAsync() as session:
        try:
            yield session
        finally:
            await session.close()
