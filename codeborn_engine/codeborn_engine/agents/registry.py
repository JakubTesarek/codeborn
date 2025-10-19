from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Awaitable, Callable
from uuid import UUID

from codeborn_shared.config import AgentsConfig
from codeborn_shared.logger import get_logger
from codeborn_shared.model import Message, Bot

if TYPE_CHECKING:
    from codeborn_engine.agents import BotAgent


class AgentRegistry:
    """Registry for managing agents."""

    def __init__(self, config: AgentsConfig, on_message: Callable[[BotAgent, Message], Awaitable[None]]) -> None:
        self._config = config
        self._logger = get_logger(component='agent_registry')
        self._agents: dict[UUID, BotAgent] = {}
        self._on_message = on_message
        self._async_lock = asyncio.Lock()

    async def add_agent(self, agent: BotAgent) -> None:
        """Register and start an agent."""
        self._logger.info('Adding agent', bot_gid=str(agent.bot.gid))

        async with self._async_lock:
            if await self.get_agent(agent.bot.gid) is not None:
                raise ValueError(f'Agent with gid "{agent.bot.gid}" already registered.')

            self._agents[agent.bot.gid] = agent
            await agent.start(self._on_message)

    async def remove_agent(self, bot_gid: UUID) -> None:
        """Stop and unregister an agent by its gid."""
        self._logger.info('Removing agent', bot_gid=str(bot_gid))
        async with self._async_lock:
            if agent := self._agents.pop(bot_gid, None):
                await agent.stop()
            else:
                raise ValueError(f'Agent with gid "{bot_gid}" not found.')

    async def remove_all(self) -> None:
        """Stop and unregister all agents."""
        await asyncio.gather(*(self.remove_agent(agent.bot.gid) for agent in await self.get_agents()))

    async def get_agents(self) -> list[BotAgent]:
        """Get a list of all registered agents."""
        async with self._async_lock:
            return list(self._agents.values())

    async def get_agent(self, bot_gid: UUID) -> BotAgent | None:
        """Get a registered agent by its bot_gid."""
        return self._agents.get(bot_gid)

    async def restart_agent(self, bot: Bot) -> BotAgent:
        """Restart an agent for a given bot."""
        if agent := await self.get_agent(bot.gid):
            await self.remove_agent(agent.bot.gid)

        agent = self._config.runtime_class(bot, self._config)  # type: ignore
        await self.add_agent(agent)
        return agent
