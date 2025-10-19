from __future__ import annotations

from typing import Any, Awaitable, Callable, TypeVar

from structlog import BoundLogger

from codeborn_shared.logger import get_logger
from codeborn_shared.model import Message
from codeborn_client.messages import MessageType

from codeborn_engine.agents import BotAgent


Route = TypeVar(
    'Route', bound=Callable[[Message, BotAgent, BoundLogger], Awaitable[dict[str, Any] | Message | None]]
)


def error_response(reason: str, **kwargs) -> dict[str, str]:
    """Generate a standard error response dictionary."""
    return {
        'status': 'error',
        'reason': reason,
        **kwargs
    }


def success_response(**kwargs) -> dict[str, str]:
    """Generate a standard success response dictionary."""
    return {
        'status': 'success',
        **kwargs
    }


class Router:
    """A simple command router."""

    def __init__(self, routers: list[Router] | None = None) -> None:
        self._logger = get_logger(component='command_router')
        self.routers = routers or []
        self.routes = {}

    def route(self, command: str) -> Callable[[Route], Route]:
        """Decorator that just prints when applied, returns the same function."""
        def decorator(func: Route) -> Route:
            self.routes[command] = func
            return func
        return decorator

    async def match(self, agent: BotAgent, message: Message) -> bool:
        """Match a command and execute the corresponding handler."""
        if route := self.routes.get(message.payload['command']):
            if response := await route(message, agent, self._logger):
                await self._respond(agent, message, response)
            return True

        for router in self.routers:
            if await router.match(agent, message):
                return True

        return False

    async def _respond(self, agent: BotAgent, message: Message, response: dict[str, Any] | Message) -> None:
        """Send a response message to the agent."""
        if isinstance(response, dict):
            response = Message(
                bot=agent.bot,
                type=MessageType.command_result,
                payload=response
            )

        response.response_to = message.gid
        await agent.send_message(response)
