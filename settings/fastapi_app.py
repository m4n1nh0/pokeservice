from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT

from database.redis import redis_conn
from schemas.auth_jwt import AuthJwtSettings
from settings.openapi import poke_openapi


@AuthJWT.load_config
def get_config():
    """JWT Token Configuration."""
    return AuthJwtSettings()


@AuthJWT.token_in_denylist_loader
def check_if_token_in_deny_list(decrypted_token):
    """JWT Verification if token exists in deny list."""
    jti = decrypted_token['jti']
    entry = redis_conn.get(jti)
    return entry and entry == 'true'


def create_app() -> FastAPI:
    """Fastapi instance creation."""
    app = FastAPI(
        title="PokeService",
        version="0.1.0",
        description="Sistema para brincar com pokemons",
        docs_url='/docs',
        redoc_url='/redoc',
        openapi_url='/openapi.json'
    )
    allow_origin = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origin,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.openapi = poke_openapi(app)

    api = "/api"

    from routers import pokemon, login, double_factor, user, health
    app.include_router(login.router, prefix=api)
    app.include_router(double_factor.router, prefix=api)
    app.include_router(user.router, prefix=api)
    app.include_router(pokemon.router, prefix=api)
    app.include_router(health.router, prefix=api)

    return app
