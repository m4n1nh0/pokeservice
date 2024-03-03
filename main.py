"""Initial file setup."""

import uvicorn

from settings.fastapi_app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
