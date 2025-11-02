from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, TYPE_CHECKING

from codeborn.logger import get_logger
from codeborn.model import Message, Bot

from codeborn.engine.agents import AsyncProcessAgent

if TYPE_CHECKING:
    from codeborn.config import AgentsConfig
    from codeborn.engine.agents import BotAgent


class DockerAgent(AsyncProcessAgent):
    """Docker container agent using subprocess I/O."""

    def __init__(self, bot: Bot, config: AgentsConfig) -> None:
        super().__init__(bot, config)

        self._docker_image = config.container_image
        self._logger = get_logger(
            agent_gid=self.bot.gid,
            agent_type='docker',
            docker_image=self._docker_image,
            entry_point=self.bot.entry_point
        )

    @property
    def container_name(self) -> str:
        """Name of the container running this process."""
        return f'agent-{self.bot.gid}'

    async def start(self, on_message: Callable[[BotAgent, Message], Awaitable[None]]) -> None:
        """Start the agent process and begin listening for messages."""
        entry_point = self.bot.entry_point_path
        engine_name = entry_point.name

        self._process = await asyncio.create_subprocess_exec(
            'docker', 'run', '--rm', '-i',
            '--name', self.container_name,
            '--network', 'none',
            '--cpus', '0.5',
            '--memory', '250m',
            '--cap-drop', 'ALL',
            '-e', 'PYTHONUNBUFFERED=0',
            '-v', f'{self.bot.entry_point_path}:/{engine_name}:ro,Z',
            '-e', 'PYTHONPATH=/',
            self._docker_image,
            'python', '-m', engine_name,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self._stdout_task = asyncio.create_task(self._listen_stdout(on_message))
        self._stderr_task = asyncio.create_task(self._listen_stderr(on_message))
        self._logger.info('Agent started.')

    async def stop(self) -> None:
        """Terminate container safely."""
        await super().stop()
        await asyncio.create_subprocess_exec('docker', 'rm', '-f', self.container_name)
