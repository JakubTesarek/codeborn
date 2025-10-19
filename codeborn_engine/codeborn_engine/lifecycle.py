import asyncio
import datetime
from typing import AsyncIterator

from codeborn_client.messages import MessageType
from codeborn_shared.config import AgentsHeartbeatConfig, AgentsRestartConfig, StateUpdateConfig
from codeborn_shared.logger import get_logger
from codeborn_shared.model import Bot, Message

from codeborn_engine.agents import BotAgent
from codeborn_engine.agents.registry import AgentRegistry


async def delay(interval: float) -> AsyncIterator[int]:
    """Yield control every `interval` seconds, keeping a fixed-rate schedule."""
    counter = 0
    loop = asyncio.get_running_loop()
    last_start: float | None = None

    try:
        while True:
            if last_start is not None:
                elapsed = loop.time() - last_start
                await asyncio.sleep(max(0, interval - elapsed))
            last_start = loop.time()
            yield counter
            counter += 1
    except asyncio.CancelledError:
        return


async def send_state_update(agent: BotAgent) -> None:
    """Send the latest world state to a given agent."""
    await agent.bot.fetch_related('armies', 'armies__units', 'armies__location')

    game_state = {
        'me': await agent.bot.dump()
    }

    message = Message(
        bot=agent.bot,
        type=MessageType.state_sync,
        payload=game_state
    )
    await agent.send_message(message)


async def heartbeat(config: AgentsHeartbeatConfig, registry: AgentRegistry) -> None:
    """Send heartbeat messages to all agents every second."""
    logger = get_logger(component='heartbeat')
    try:
        logger.info('Started')

        async for _ in delay(config.interval):
            for agent in await registry.get_agents():
                heartbeat_age = agent.bot.heartbeat_age.total_seconds() if agent.bot.heartbeat_age else None
                if not agent.is_alive:
                    logger.warning(
                        'Agent not running.',
                        bot_gid=agent.bot.gid,
                        heartbeat_age=heartbeat_age
                    )
                    await registry.remove_agent(agent.bot.gid)

                elif heartbeat_age is not None and heartbeat_age > config.timeout:
                    logger.warning(
                        'Agent heartbeat timeout.',
                        bot_gid=agent.bot.gid,
                        heartbeat_age=heartbeat_age
                    )
                    await registry.remove_agent(agent.bot.gid)

                else:
                    message = Message(
                        bot=agent.bot,
                        type=MessageType.heartbeat_request,
                    )
                    await agent.send_message(message)
    finally:
        logger.info('Stopped.')


async def restart(config: AgentsRestartConfig, registry: AgentRegistry) -> None:
    """Check agents that need to be restarted every interval."""
    logger = get_logger(component='restart')

    async def restart_agent(user: Bot) -> None:
        """Restart an agent for a given user."""
        agent = await registry.restart_agent(user)
        await send_state_update(agent)  # Send initial state update early
        user.restart_requested = False
        user.start_at = datetime.datetime.now(datetime.timezone.utc)
        user.last_heartbeat = None  # type: ignore
        await user.save(update_fields=['restart_requested', 'start_at', 'last_heartbeat'])

    try:
        logger.info('Started')

        async for _ in delay(config.interval):
            for bot in await Bot.all():
                if not bot.enabled:
                    if await registry.get_agent(bot.gid) is not None:
                        logger.info('Stopping disabled agent.', bot_gid=str(bot.gid), bot_name=bot.entry_point)
                        await registry.remove_agent(bot.gid)
                    else:
                        logger.info('Skipping disabled agent.', bot_gid=str(bot.gid), bot_name=bot.entry_point)
                elif bot.restart_requested:
                    logger.info('Restart requested.', bot_gid=str(bot.gid), bot_name=bot.entry_point)
                    await restart_agent(bot)
                elif not await registry.get_agent(bot.gid):
                    logger.info('Starting missing agent.', bot_gid=str(bot.gid), bot_name=bot.entry_point)
                    await restart_agent(bot)

    finally:
        logger.info('Stopped.')


async def state_update(config: StateUpdateConfig, registry: AgentRegistry):
    """Periodically update all bots with the latest world state."""
    logger = get_logger(component='state_update')
    try:
        logger.info('Started')

        async for _ in delay(config.interval):
            for agent in await registry.get_agents():
                await send_state_update(agent)
    finally:
        logger.info('Stopped.')
