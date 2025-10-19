from __future__ import annotations

import abc
import datetime
import asyncio
import contextlib
from collections.abc import Awaitable
from typing import Callable, TYPE_CHECKING

from codeborn_shared.logger import get_logger
from codeborn_shared.model import Message, Bot

if TYPE_CHECKING:
    from codeborn_shared.config import AgentsConfig


class BotAgent(abc.ABC):
    bot: Bot

    @property
    @abc.abstractmethod
    def is_alive(self) -> bool:
        """Check if the agent is alive."""

    @abc.abstractmethod
    async def start(self, on_message: Callable[[BotAgent, Message], Awaitable[None]]) -> None:
        """Start the agent."""

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop the agent."""

    @abc.abstractmethod
    async def send_message(self, message: Message) -> None:
        """Send a message to the agent."""


class AsyncProcessAgent(BotAgent, abc.ABC):
    """An agent that runs as a separate process."""

    def __init__(self, bot: Bot, config: AgentsConfig) -> None:
        self.bot = bot
        self.config = config

        self.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)

        self._logger = get_logger(bot_gid=str(self.bot.gid))
        self._process: asyncio.subprocess.Process | None = None
        self._stdout_task: asyncio.Task | None = None
        self._stderr_task: asyncio.Task | None = None

    @property
    def is_alive(self) -> bool:
        return self._process is not None and self._process.returncode is None

    async def send_message(self, message: Message) -> None:
        """Send a message to the agent process."""
        if self._process and self._process.stdin:
            try:
                self._process.stdin.write(message.to_bytes())
                await self._process.stdin.drain()
                self._logger.debug('Sent message', raw=message)
            except Exception as exc:
                self._logger.warning(f'Failed to send message: {exc!r}')
        else:
            self._logger.warning('Stdin unavailable, cannot send message.')

    async def _listen_stdout(self, on_message: Callable[[BotAgent, Message], Awaitable[None]]) -> None:
        """Read stdout and decode messages."""
        assert self._process and self._process.stdout
        while not self._process.stdout.at_eof():
            if message_bytes := await self._process.stdout.readline():
                try:
                    message = Message.from_bytes(self.bot.gid, message_bytes)
                    await on_message(self, message)
                except Exception as exc:
                    self._logger.error('Stdout parsing error.', exc_info=exc, raw=message_bytes)
            else:
                break

    async def _listen_stderr(self, on_message: Callable[[BotAgent, Message], Awaitable[None]]) -> None:
        """Read and log stderr lines separately."""
        assert self._process and self._process.stderr
        while not self._process.stderr.at_eof():
            if message_bytes := await self._process.stderr.readline():
                try:
                    message = Message.from_bytes(self.bot.gid, message_bytes)
                    await on_message(self, message)
                except Exception as exc:
                    self._logger.error('Stderr parsing error.', exc_info=exc, raw=message_bytes)
            else:
                break

    async def stop(self) -> None:
        """Terminate process safely."""
        if self._process:
            self._logger.info('Stopping agent')

            for task in (self._stdout_task, self._stderr_task):
                if task:
                    task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await task

            try:
                if self._process.returncode is None:
                    self._process.terminate()
                    with contextlib.suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(self._process.wait(), timeout=3)
            except asyncio.TimeoutError:
                self._logger.warning('Process did not terminate gracefully, killing it.')
                with contextlib.suppress(ProcessLookupError):
                    self._process.kill()
                    await self._process.wait()
            except ProcessLookupError:
                self._logger.warning('Process already terminated')
            except Exception as exc:
                self._logger.warning('Error while stopping container', exc_info=exc)
            finally:
                self._process = None
                self._logger.info('Agent stopped')
