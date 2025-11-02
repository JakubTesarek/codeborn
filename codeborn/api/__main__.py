from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from codeborn.config import get_config
from codeborn.database import db
from codeborn.api.auth import init_oauth
from codeborn.api.endpoints import home, healthcheck, auth, repos, bots


config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    app.state.config = config
    app.state.oauth = init_oauth(config.github)
    async with db(config.database):
        yield


app = FastAPI(title=config.api.app_name, lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=config.api.session_key)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.api.frontend_url],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(home.router)
app.include_router(healthcheck.router, prefix='/api', tags=['Healthcheck'])
app.include_router(auth.router, prefix='/api/auth', tags=['Authentication'])
app.include_router(repos.router, prefix='/api/repos', tags=['Repositories'])
app.include_router(bots.router, prefix='/api/bots', tags=['Bots'])


if __name__ == '__main__':
    uvicorn.run(
        'codeborn.api.__main__:app',
        host=config.api.host,
        port=config.api.port,
        reload=config.api.auto_reload
    )
