from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

from codeborn.model import Bot, BotMemory, GitHubAccount, GithubRepo, User, Message
from codeborn.api.auth import get_current_user


router = APIRouter()


class BotCreateRequest(BaseModel):
    """Request model for creating a new bot."""

    name: str
    repo_gid: str
    enabled: bool


@router.get('/')
async def get_all(user: User = Depends(get_current_user)) -> dict:
    """Get all GitHub repositories for the current user."""
    bots = await user.bots.all()
    return {'bots': [await bot.dump(exclude={'armies'}) for bot in bots]}


@router.post('/')
async def create(request: BotCreateRequest, user: User = Depends(get_current_user)) -> dict:
    """Create a new bot for the current user."""
    repo = await GithubRepo.get_or_none(gid=request.repo_gid).prefetch_related('github_account')
    if not repo or repo.github_account.user_id != user.gid:
        raise HTTPException(status_code=404, detail='Repository not found')

    bot = Bot(
        user=user,
        name=request.name,
        entry_point=repo.full_name,
        enabled=request.enabled
    )
    await bot.save()

    memory = BotMemory(bot=bot)
    await memory.save()

    return await bot.dump(exclude={'armies'})


@router.post('/{bot_gid}/restart')
async def restart(bot_gid: UUID, user: User = Depends(get_current_user)) -> dict:
    """Restart a bot by its GID."""
    try:
        bot = await Bot.get(user=user, gid=bot_gid)
        bot.restart_requested = True
        await bot.save(update_fields=['restart_requested'])
        return await bot.dump(exclude={'armies'})
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail='Bot not found') from e


@router.post('/{bot_gid}/disable')
async def disable(bot_gid: UUID, user: User = Depends(get_current_user)) -> dict:
    """Disable a bot by its GID."""
    try:
        bot = await Bot.get(user=user, gid=bot_gid)
        bot.enabled = False
        bot.restart_requested = False
        await bot.save(update_fields=['enabled', 'restart_requested'])
        return await bot.dump(exclude={'armies'})
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail='Bot not found') from e


@router.post('/{bot_gid}/enable')
async def enable(bot_gid: UUID, user: User = Depends(get_current_user)) -> dict:
    """Enable a bot by its GID."""
    try:
        bot = await Bot.get(user=user, gid=bot_gid)
        bot.enabled = True
        bot.restart_requested = True
        await bot.save(update_fields=['enabled', 'restart_requested'])
        return await bot.dump(exclude={'armies'})
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail='Bot not found') from e


@router.get('/{bot_gid}/messages')
async def get_messages(
    bot_gid: UUID,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
) -> dict:
    """Return recent messages for a bot, newest first."""
    if bot := await Bot.filter(user=user, gid=bot_gid).first():
        total = await Message.filter(bot=bot).count()
        messages_query = (
            Message.filter(bot=bot)
            .order_by('-datetime')
            .offset(offset)
            .limit(limit)
        )
        messages = [await msg.dump() for msg in await messages_query]
        return {'messages': messages, 'total': total}
    else:
        raise HTTPException(status_code=404, detail='Bot not found')



@router.get('/{bot_gid}/memory')
async def get_memory(bot_gid: UUID, user: User = Depends(get_current_user)) -> dict:
    """Return recent messages for a bot, newest first."""
    if memory := await BotMemory.filter(bot__gid=bot_gid, bot__user=user).first():
        return await memory.dump()
    else:
        raise HTTPException(status_code=404, detail='Bot not found')


@router.get('/eligibility')
async def eligibility(user: User = Depends(get_current_user)) -> dict:
    """Get all GitHub repositories for the current user."""
    github_account = await GitHubAccount.get(user=user).prefetch_related('repos')
    repos = await GithubRepo.filter(github_account=github_account).all()

    return {
        'max_bots': user.max_bots,
        'repos': [await repo.dump() for repo in repos if repo.local_version is not None],
    }
