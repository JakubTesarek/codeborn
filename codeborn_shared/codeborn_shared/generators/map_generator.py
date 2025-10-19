import asyncio

from codeborn_shared.logger import get_logger, init_logging
from codeborn_shared.model import Location
from codeborn_shared.database import init_db, close_db
from codeborn_shared.config import CodebornConfig, get_config


async def main(config: CodebornConfig) -> None:
    await init_db(config.database)
    map_config = config.generators.map
    logger = get_logger(component='map_generator')

    try:
        logger.info('Removing old map.')
        await Location.all().delete()

        logger.info('Generating map.', width=map_config.width, height=map_config.height)
        for y in range(map_config.width):
            for x in range(map_config.height):
                loc = Location(x=x, y=y)
                await loc.save()
    finally:
        await close_db()


if __name__ == '__main__':
    config = get_config()
    init_logging(config.logging)
    asyncio.run(main(config))
