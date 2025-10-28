from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING, Callable
from collections.abc import Awaitable

from codeborn import to_abs_path
from codeborn.logger import get_logger
from codeborn.model import Message, Bot

from codeborn.engine.agents import AsyncProcessAgent

if TYPE_CHECKING:
    from codeborn.config import AgentsConfig
    from codeborn.engine.agents import BotAgent


class ProcessAgent(AsyncProcessAgent):
    """An agent that runs as a separate process."""

    def __init__(self, bot: Bot, config: AgentsConfig) -> None:
        super().__init__(bot, config)

        self._logger = get_logger(
            bot_gid=str(self.bot.gid),
            agent_type='process',
            entry_point=self.bot.entry_point
        )

    async def start(self, on_message: Callable[[BotAgent, Message], Awaitable[None]]) -> None:
        """Start the agent process and begin listening for messages."""
        module_path = to_abs_path(self.bot.entry_point)
        self._process = await asyncio.create_subprocess_exec(
            sys.executable, '-m', module_path.name,
            cwd=module_path.parent,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self._stdout_task = asyncio.create_task(self._listen_stdout(on_message))
        self._stderr_task = asyncio.create_task(self._listen_stderr(on_message))
        self._logger.info('Agent started')
