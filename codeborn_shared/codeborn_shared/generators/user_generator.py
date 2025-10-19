import asyncio

from codeborn_shared.logger import get_logger, init_logging
from codeborn_shared.model import Army, User, Location, Unit, Bot
from codeborn_shared.database import init_db, close_db
from codeborn_shared.config import CodebornConfig, get_config


async def main(config: CodebornConfig) -> None:
    await init_db(config.database)
    logger = get_logger(component='user_generator')

    try:
        user = await User.first()

        logger.info('Generating bot.')
        bot = Bot(user=user, entry_point='user_bots/noop')
        await bot.save()

        logger.info('Generating army.')
        location = await Location.get(
            x=config.generators.map.width // 2,
            y=config.generators.map.height // 2
        )

        army = Army(bot=bot, location=location)
        await army.save()

        logger.info('Generating unit.')
        light_infantry = Unit(army=army, type='light_infantry', count=50, stamina_snapshot=0.0)
        heavy_infantry = Unit(army=army, type='heavy_infantry', count=10, stamina_snapshot=0.0)
        await light_infantry.save()
        await heavy_infantry.save()

    finally:
        await close_db()


if __name__ == '__main__':
    config = get_config()
    init_logging(config.logging)
    asyncio.run(main(config))
