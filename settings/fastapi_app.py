from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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

    api = "/api"

    from routers import pokemon
    app.include_router(pokemon.router, prefix=api)

    return app
