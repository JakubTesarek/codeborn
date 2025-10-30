from fastapi import APIRouter, Request, Depends, Response
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from tortoise.exceptions import DoesNotExist

from codeborn.config import CodebornConfig
from codeborn.model import User, GitHubAccount
from codeborn.api.auth import create_token, get_current_user
from codeborn.api.repos import refresh_repos
from codeborn.api.deps import get_config, get_oauth


router = APIRouter()


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
        secure=False,
        samesite='lax',
        max_age=config.auth.jwt.ttl
    )
    return response


@router.get('/me')
async def me(user: User = Depends(get_current_user)) -> dict:
    """Get the current authenticated user's information."""
    return await user.dump(exclude={'bots', 'github__repos'})


@router.post('/logout')
async def logout() -> Response:
    """Logout the current user by deleting the auth cookie."""
    resp = Response(status_code=204)
    resp.delete_cookie(
        key='auth_token',
        path='/',
        samesite='lax',
        secure=False,
    )
    return resp
