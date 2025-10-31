from pathlib import Path
import shutil
from fastapi import APIRouter, Request, Depends, Response, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from tortoise.exceptions import DoesNotExist
from pydantic import BaseModel

from codeborn.config import CodebornConfig
from codeborn.model import User, GitHubAccount
from codeborn.api.auth import create_token, get_current_user
from codeborn.api.repos import refresh_repos
from codeborn.api.deps import get_config, get_oauth


router = APIRouter()


class AccountDeleteRequest(BaseModel):
    """Request model for removing account."""

    username: str


async def get_logout_response(config: CodebornConfig) -> Response:
    """Get a response removing auth cookie"""
    response = Response(status_code=204)
    response.delete_cookie(
        key='auth_token',
        domain=config.auth.cookie_domain,
        path='/',
        samesite='lax',
        secure=config.auth.secure_cookie,
    )
    return response


@router.get('/github/login')
async def github_login(
    request: Request,
    oauth: OAuth = Depends(get_oauth),
    config: CodebornConfig = Depends(get_config)
) -> RedirectResponse:
    """Redirect to GitHub for authentication."""
    return await oauth.github.authorize_redirect(request, config.github.redirect_url)  # type: ignore


@router.get('/github/callback')
async def github_callback(
    request: Request,
    oauth: OAuth = Depends(get_oauth),
    config: CodebornConfig = Depends(get_config),
) -> RedirectResponse:
    """Handle the callback from GitHub after authentication."""
    token = await oauth.github.authorize_access_token(request)  # type: ignore
    user_data = (await oauth.github.get('user', token=token)).json()  # type: ignore

    github_id = user_data['id']
    login = user_data['login']

    try:
        github_account = await GitHubAccount.get(github_id=github_id).prefetch_related('user')
        github_account.access_token = token['access_token']
        github_account.token_type = token['token_type']
        github_account.scope = token.get('scope', '')
        github_account.avatar_url = user_data.get('avatar_url')
        await github_account.save()
        user = github_account.user
    except DoesNotExist:
        user = await User.create()
        github_account = await GitHubAccount.create(
            user=user,
            github_id=github_id,
            login=login,
            access_token=token['access_token'],
            token_type=token['token_type'],
            scope=token.get('scope', ''),
            avatar_url=user_data.get('avatar_url'),
        )
        await refresh_repos(github_account)

    response = RedirectResponse(config.api.frontend_url)
    response.set_cookie(
        key='auth_token',
        domain=config.auth.cookie_domain,
        path='/',
        value=create_token(str(user.gid), config.auth.jwt),
        httponly=True,
        secure=config.auth.secure_cookie,
        samesite='lax',
        max_age=config.auth.jwt.ttl
    )
    return response


@router.get('/me')
async def get_account(user: User = Depends(get_current_user)) -> dict:
    """Get the current authenticated user's information."""
    return await user.dump(exclude={'bots', 'github__repos'})


@router.delete('/me')
async def delete_account(
    request: AccountDeleteRequest,
    user: User = Depends(get_current_user),
    config: CodebornConfig = Depends(get_config)
) -> Response:
    """Remove the current authenticated user."""
    github_login = (await user.github).login  # type: ignore

    if request.username == github_login:
        user_dir = Path(config.agents.base_dir).expanduser() / github_login
        if user_dir.exists():
            shutil.rmtree(user_dir)
        await user.delete()
        return await get_logout_response(config)

    raise HTTPException(status_code=400, detail="Username doesn't match.")


@router.post('/logout')
async def logout(config: CodebornConfig = Depends(get_config)) -> Response:
    """Logout the current user by deleting the auth cookie."""
    return await get_logout_response(config)
