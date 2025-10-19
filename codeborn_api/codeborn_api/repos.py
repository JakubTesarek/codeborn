import contextlib
from datetime import datetime, timezone

from configobj import ConfigObj
from github.GithubException import GithubException
import git

from codeborn_shared.config import get_config
from codeborn_shared.model import GitHubAccount, GithubRepo


async def refresh_repos(github_account: GitHubAccount) -> None:
    """Refresh GitHub repositories for a given user."""
    repo_ids = set()

    for gh_repo in github_account.gh_user.get_repos():
        if gh_repo.archived or gh_repo.disabled:
            continue

        version = None
        repo_ids.add(gh_repo.id)

        with contextlib.suppress(GithubException):
            ini_file = gh_repo.get_contents(get_config().agents.version_file)
            content = ini_file.decoded_content.decode()
            ini_config = ConfigObj(content.splitlines())
            version = ini_config.get('version', None)

        await GithubRepo.update_or_create(
            github_id=gh_repo.id,
            defaults={
                'github_id': gh_repo.id,
                'github_account': github_account,
                'name': gh_repo.name,
                'full_name': gh_repo.full_name,
                'size': gh_repo.size,
                'clone_url': gh_repo.clone_url,
                'html_url': gh_repo.html_url,
                'remote_version': version,
                'remote_sha': gh_repo.get_commits()[0].sha[:7],
            }
        )

    await GithubRepo.filter(github_account=github_account).exclude(github_id__in=repo_ids).delete()
    github_account.last_update = datetime.now(timezone.utc)
    await github_account.save()


async def pull_repo(repo: GithubRepo) -> None:
    """Pull updates for a cloned GitHub repository."""
    if local_repo := repo.local_repo:
        local_repo.remotes.origin.pull()
    else:
        raise ValueError('Repository is not cloned locally.')


async def clone_repo(repo: GithubRepo) -> None:
    """Clone a GitHub repository."""
    await repo.fetch_related('github_account')
    github_account = repo.github_account
    auth_url = repo.clone_url.replace('https://', f'https://{github_account.access_token}@')

    git.Repo.clone_from(auth_url, repo.local_clone_path, depth=1)
