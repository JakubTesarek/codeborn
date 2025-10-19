from uuid import UUID
from fastapi import APIRouter, Depends

from codeborn_api.auth import get_current_user
from codeborn_api.repos import clone_repo, pull_repo, refresh_repos
from codeborn_shared.model import GithubRepo, User, GitHubAccount, dump_dt


router = APIRouter()


async def get_repos_response(user: User) -> dict:
    """Get GitHub repositories for the current user."""
    github_account = await GitHubAccount.get(user=user).prefetch_related('repos')
    repos = await GithubRepo.filter(github_account=github_account).all()

    repos.sort(
        key=lambda r: (
            r.local_version is None,
            r.remote_version is None,
            r.name.lower(),
        )
    )

    return {
        'last_update': dump_dt(github_account.last_update),
        'repos': [await repo.dump() for repo in repos],
    }


@router.get('/')
async def get_all(user: User = Depends(get_current_user)) -> dict:
    """Get all GitHub repositories for the current user."""
    return await get_repos_response(user)


@router.post('/refresh')
async def refresh(user: User = Depends(get_current_user)) -> dict:
    """Refresh GitHub repositories for the current user."""
    github_account = await GitHubAccount.get(user=user).prefetch_related('repos')
    await refresh_repos(github_account)
    return await get_repos_response(user)


@router.post('/{repo_gid}/update')
async def clone_or_pull(repo_gid: UUID, user: User = Depends(get_current_user)) -> dict:
    """Clone or pull a GitHub repository by its GID."""
    github_account = await GitHubAccount.get(user=user)
    repo = await GithubRepo.get(gid=repo_gid, github_account=github_account)
    if repo.is_cloned:
        await pull_repo(repo)
    else:
        await clone_repo(repo)

    return await repo.dump()
