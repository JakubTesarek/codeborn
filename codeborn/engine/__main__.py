import asyncio

from codeborn.client.messages import MessageType
from codeborn.database import db
from codeborn.config import CodebornConfig, get_config
from codeborn.logger import get_logger, init_logging
from codeborn.model import BotMemory, Message
from codeborn.engine import lifecycle
from codeborn.engine.agents.registry import AgentRegistry
from codeborn.engine.agents import BotAgent
from codeborn.engine.commands import Router


class MessageDispatcher:
    """Manager of bot messages."""

    def __init__(self, router: Router) -> None:
        self._logger = get_logger(component='message_dispatcher')
        self._router = router

    async def _log_heartbeat(self, agent: BotAgent, message: Message) -> None:
        """Log a heartbeat message to the database."""
        await agent.bot.refresh_from_db()
        agent.bot.last_heartbeat = message.datetime
        await agent.bot.save(update_fields=['last_heartbeat'])

    async def _save_memory(self, agent: BotAgent, message: Message) -> None:
        """Save memory upload to the database."""
        await BotMemory.filter(bot=agent.bot).update(
            data=message.payload['data'],
            updated_at=message.datetime
        )

    async def on_message(self, agent: BotAgent, message: Message) -> None:
        """Handle messages received from bots."""
        await message.save()

        match message.type:
            case MessageType.heartbeat_response:
                await self._log_heartbeat(agent, message)
            case MessageType.bot_log:
                self._logger.debug('Received log', raw=message, payload=message.payload['text'])
            case MessageType.memory_upload:
                self._logger.debug('Received memory dump', raw=message)
                await self._save_memory(agent, message)
            case MessageType.command:
                self._logger.debug('Received command', bot_gid=agent.bot.gid, payload=message.payload)
                matched = await self._router.match(agent, message)
                if not matched:
                    self._logger.warning('No command handler matched.', bot_gid=agent.bot.gid, payload=message.payload)
            case _:
                self._logger.warning('Received unknown message type.', bot_gid=agent.bot.gid, message_type=message.type)


async def main(config: CodebornConfig) -> None:
    """Main entry point for the engine."""
    logger = get_logger(component='main')

    async with db(config.database):
        from codeborn.engine.commands.army import router as army_router  # import after logger init
        message_dispatcher = MessageDispatcher(army_router)
        agent_registry = AgentRegistry(config.agents, message_dispatcher.on_message)

        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(lifecycle.restart(config.lifecycle.restart, agent_registry))
                tg.create_task(lifecycle.heartbeat(config.lifecycle.heartbeat, agent_registry))
                tg.create_task(lifecycle.state_update(config.lifecycle.state_update, agent_registry))
        except Exception as exc:
            logger.exception('TaskGroup crashed cancelled', exc_info=exc)
        finally:
            logger.info('Stopping all agents')
            await agent_registry.remove_all()


if __name__ == '__main__':
    config = get_config()
    init_logging(config.logging)
    logger = get_logger(component='main')

    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        logger.info('Shutting down (keyboard interrupt)')
    except asyncio.CancelledError:
        logger.info('Cancelled remaining tasks')
    except Exception as exc:
        logger.exception('Unhandled exception', exc_info=exc)
