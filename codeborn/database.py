from contextlib import asynccontextmanager
from typing import AsyncIterator

from tortoise import Tortoise

from codeborn.config import DatabaseConfig, get_config
from codeborn.logger import get_logger


AERICH_CONFIG = get_config().database.tortoise_config  # For Aerich migrations


async def init_db(config: DatabaseConfig) -> None:
    """Initialize the database connection."""
    logger = get_logger(component='database')
    logger.info('Initializing database connection.')
    await Tortoise.init(config=config.tortoise_config)
    if config.init_schema:
        logger.info('Generating database schema.')
        await Tortoise.generate_schemas()


async def close_db() -> None:
    """Close all database connections."""
    logger = get_logger(component='database')
    await Tortoise.close_connections()
    logger.info('Closing database connections.')


@asynccontextmanager
async def db(config: DatabaseConfig) -> AsyncIterator[None]:
    """Async context manager for database connection."""
    await init_db(config)
    try:
        yield
    finally:
        await close_db()
