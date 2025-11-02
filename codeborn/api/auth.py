from __future__ import annotations

from datetime import datetime, timezone, timedelta

import jwt
from fastapi import Depends, HTTPException, Request
from authlib.integrations.starlette_client import OAuth

from codeborn.config import GithubConfig, JwtConfig, CodebornConfig
from codeborn.api.deps import get_config
from codeborn.model import User


def init_oauth(config: GithubConfig) -> OAuth:
    """Register OAuth clients."""
    oauth = OAuth()
    oauth.register(
        name='github',
        client_id=config.client_id,
        client_secret=config.client_secret,
        access_token_url=str(config.access_token_url),
        authorize_url=str(config.authorize_url),
        api_base_url=str(config.api_base_url),
        client_kwargs={'scope': config.scope},
    )

    return oauth


def create_token(user_id: str, config: JwtConfig) -> str:
    """Create a JWT token for the given user ID."""
    payload = {
        'sub': str(user_id),
        'exp': datetime.now(timezone.utc) + timedelta(seconds=config.ttl),
    }
    return jwt.encode(payload, config.secret, algorithm=config.algorithm)


def verify_token(token: str, config: JwtConfig) -> dict | None:
    """Verify the given JWT token and return the payload if valid."""
    try:
        return jwt.decode(token, config.secret, algorithms=[config.algorithm])
    except jwt.PyJWTError:
        return None


async def get_current_user(request: Request, config: CodebornConfig = Depends(get_config)) -> User:
    """Get the current authenticated user based on the auth token in cookies."""
    if not (token := request.cookies.get('auth_token')):
        raise HTTPException(status_code=401, detail='Missing auth token')

    if not (token_data := verify_token(token, config.auth.jwt)):
        raise HTTPException(status_code=401, detail='Invalid or expired token')

    if not (user := await User.get_or_none(gid=token_data['sub'])):
        raise HTTPException(status_code=404, detail='User not found')

    request.state.user = user
    return user
